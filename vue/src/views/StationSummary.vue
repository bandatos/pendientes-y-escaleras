<script setup>
import { ref, computed } from 'vue'
import { useSurveyStore } from '../stores/surveyStore'
import { useSyncStore } from '../stores/syncStore'
import { useImageStore } from '../stores/imageStore'
import { useSnackbarStore } from '../stores/snackbarStore'
import { IndexedDBService } from '../services/indexDB.js'
import UploadImage from '../components/UploadImage.vue'

const emit = defineEmits(['save-complete', 'back'])

// Stores
const surveyStore = useSurveyStore()
const syncStore = useSyncStore()
const imageStore = useImageStore()
const snackbarStore = useSnackbarStore()

// Estado local
const expandedPanels = ref([0]) // Primer panel abierto por defecto
const newCodes = ref({}) // Códigos temporales por escalera

// Computed
const connectionStatus = computed(() =>
  syncStore.isOnline ? '🟢 Conectado' : '🔴 Sin conexión'
)

const pendingCount = computed(() => syncStore.syncStats.pending)

// Obtener color del estado de escalera
const getStairStatusColor = (stair) => {
  if (stair.status === 'pending') return 'grey'
  return stair.isWorking ? 'success' : 'error'
}

// Obtener icono del estado
const getStairStatusIcon = (stair) => {
  if (stair.status === 'pending') return 'circle'
  return stair.isWorking ? 'check_circle' : 'cancel'
}

// Agregar código de identificación
const addCode = (stairIndex) => {
  const code = newCodes.value[stairIndex]
  if (code?.trim()) {
    if (!surveyStore.currentSurvey.stairs[stairIndex].identificationCodes) {
      surveyStore.currentSurvey.stairs[stairIndex].identificationCodes = []
    }
    surveyStore.currentSurvey.stairs[stairIndex].identificationCodes.push(
      code.trim())
    newCodes.value[stairIndex] = ''
  }
}

// Remover código
const removeCode = (stairIndex, codeIndex) => {
  surveyStore.currentSurvey.stairs[stairIndex].identificationCodes.splice(
    codeIndex, 1)
}

// Marcar escalera como completada
const markStairComplete = (stairIndex) => {
  const stair = surveyStore.currentSurvey.stairs[stairIndex]

  // Validaciones básicas
  // Solo validar códigos si hasCodes no está explícitamente marcado como true (sin códigos)
  const hasNoCodes = stair.hasCodes === true
  const hasCodesEmpty = !stair.identificationCodes || stair.identificationCodes.length === 0

  if (!hasNoCodes && hasCodesEmpty) {
    snackbarStore.showWarning('Agrega al menos un código de identificación o marca que no hay códigos visibles')
    return
  }

  if (!stair.connectionPoints?.pointA?.trim()) {
    snackbarStore.showWarning('Especifica el punto A de conexión')
    return
  }

  if (stair.isWorking === null) {
    snackbarStore.showWarning('Indica si la escalera funciona')
    return
  }

  // Marcar como completada
  stair.status = 'completed'

  // Cerrar panel actual y abrir siguiente (si existe)
  const currentIndex = expandedPanels.value.indexOf(stairIndex)
  if (currentIndex > -1) {
    expandedPanels.value.splice(currentIndex, 1)
  }

  if (stairIndex < surveyStore.totalStairs - 1) {
    expandedPanels.value.push(stairIndex + 1)
  }
}

// Guardar datos completos
const handleSave = async () => {
  try {
    // Validar que todas las escaleras estén completadas
    const allCompleted = surveyStore.currentSurvey.stairs.every(
      s => s.status === 'completed'
    )

    if (!allCompleted) {
      snackbarStore.showWarning('Debes completar todas las escaleras antes de guardar')
      return
    }

    // 1. Guardar registro de estación en IndexedDB
    const savedRecord = await surveyStore.completeSurvey()

    // 2. Guardar imágenes de cada escalera
    for (let stairIndex = 0; stairIndex < surveyStore.totalStairs; stairIndex++) {
      const photos = imageStore.getStairPhotos(stairIndex)

      if (photos && photos.length > 0) {
        await IndexedDBService.saveStairImages(
          savedRecord.id,
          stairIndex + 1, // stairNumber es 1-based
          photos
        )
        console.log(`📸 ${photos.length}
          imágenes guardadas para escalera ${stairIndex + 1}`)
      }
    }

    // 3. Limpiar el imageStore
    imageStore.clearSelection()

    console.log('✅ Estación y todas las imágenes guardadas exitosamente')

    emit('save-complete')

  } catch (error) {
    console.error('Error guardando:', error)
    snackbarStore.showError('Error al guardar los datos')
  }
}

// Volver a selector
const handleBack = () => {
  if (confirm('¿Seguro que quieres salir? Se perderá el progreso no guardado')) {
    surveyStore.cancelSurvey()
    emit('back')
  }
}
</script>

<template>
  <v-container fluid class="fill-height pa-0">
    <v-row no-gutters class="fill-height">
      <v-col cols="12">
        <!-- Header con status -->
        <v-card class="rounded-0" variant="flat" color="grey-lighten-5">
          <v-card-text>
            <div class="d-flex justify-space-between align-center mb-2">
              <span class="text-body-2">{{ connectionStatus }}</span>
              <span v-if="pendingCount > 0" class="text-warning text-body-2">
                📋 {{ pendingCount }} pendientes
              </span>
            </div>

            <!-- Estación seleccionada -->
            <div class="d-flex align-center">
              <v-chip
                :style="{
                  backgroundColor: surveyStore.currentSurvey?.lineColor,
                  color: 'white',
                }"
                class="mr-2"
                size="small"
              >
                {{ surveyStore.currentSurvey?.line }}
              </v-chip>
              <h2 class="text-subtitle-1 font-weight-bold">
                Estación {{ surveyStore.currentSurvey?.stationName }}
              </h2>
              <v-btn
                icon="close"
                size="small"
                variant="text"
                @click="handleBack"
                class="ml-auto"
              ></v-btn>
            </div>
          </v-card-text>
        </v-card>

        <!-- Estadísticas -->
        <v-card class="rounded-0" variant="flat">
          <v-card-text class="py-3">
            <div class="d-flex justify-space-around text-center">
              <div>
                <div class="text-h6">{{ surveyStore.totalStairs }}</div>
                <div class="text-caption text-medium-emphasis">
                  escaleras en total
                </div>
              </div>
              <v-divider vertical></v-divider>
              <div>
                <div class="text-h6 text-success">
                  {{ surveyStore.stats.working }}
                </div>
                <div class="text-caption text-medium-emphasis">funcionan</div>
              </div>
              <v-divider vertical></v-divider>
              <div>
                <div class="text-h6 text-error">
                  {{ surveyStore.stats.notWorking }}
                </div>
                <div class="text-caption text-medium-emphasis">
                  no funcionan
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>

        <v-divider></v-divider>
        <v-card-subtitle>
          Completa la info en el orden en el que recorras la estación
        </v-card-subtitle>

        <!-- Expansion Panels de Escaleras -->
        <v-expansion-panels v-model="expandedPanels" multiple>
          <v-expansion-panel
            v-for="(stair, index) in surveyStore.currentSurvey?.stairs"
            :key="index"
            :value="index"
          >
            <!-- Panel Title -->
            <v-expansion-panel-title color="grey-lighten-4">
              <div class="d-flex align-center w-100">
                <v-icon :color="getStairStatusColor(stair)" class="mr-3">
                  {{ getStairStatusIcon(stair) }}
                </v-icon>
                <div>
                  <div class="font-weight-bold">
                    Escalera {{ stair.stairNumber }}
                  </div>
                  <div
                    v-if="stair.status === 'completed'"
                    class="text-caption text-medium-emphasis"
                  >
                    {{ stair.isWorking ? "Funciona" : "No funciona" }}
                    <span v-if="stair.photoIds?.length > 0">
                      • 📷 {{ stair.photoIds.length }}
                    </span>
                  </div>
                  <div class="text-caption text-warning" v-else>Pendiente</div>
                </div>
              </div>
            </v-expansion-panel-title>

            <!-- Panel Content - Formulario completo -->
            <v-expansion-panel-text>
              <v-card flat>
                <v-card-text>
                  <!-- Nota informativa -->
                  <v-alert
                    type="info"
                    variant="tonal"
                    density="compact"
                    class="mb-4"
                  >
                    Toma en cuenta que pueden tener varios identificadores
                  </v-alert>

                  <!-- Códigos de identificación -->
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">
                      Códigos de identificación
                      <v-icon size="small" class="ml-1">
                        help_outline
                        <v-tooltip activator="parent" location="left">
                          Por ejemplo: KSG3-43, ALT-01, etc.
                        </v-tooltip>
                      </v-icon>
                    </label>

                    <div class="d-flex gap-2 mb-2">
                      <v-text-field
                        v-model="newCodes[index]"
                        variant="outlined"
                        density="compact"
                        placeholder="Ej: KSG3-43"
                        hide-details
                        @keyup.enter="addCode(index)"
                      ></v-text-field>
                      <v-btn
                        color="primary"
                        size="small"
                        icon
                        @click="addCode(index)"
                      >
                        <v-icon size="large"> add </v-icon>
                      </v-btn>
                    </div>

                    <v-checkbox
                      v-if="
                        !stair.identificationCodes ||
                        stair.identificationCodes.length === 0
                      "
                      v-model="stair.hasCodes"
                      color="error"
                      variant="text"
                      size="small"
                      class="mb-2"
                      hide-details
                      label="No hay visible ningún código"
                    >
                    </v-checkbox>
                    <div class="d-flex flex-wrap gap-2">
                      <v-chip
                        v-for="(code, codeIndex) in stair.identificationCodes"
                        :key="codeIndex"
                        closable
                        @click:close="removeCode(index, codeIndex)"
                        color="primary"
                        variant="outlined"
                        size="small"
                      >
                        {{ code }}
                      </v-chip>
                    </div>
                  </div>

                  <!-- Puntos de conexión -->
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">
                      ¿Qué puntos o nodos comunica la escalera?
                      <v-tooltip location="top">
                        <template v-slot:activator="{ props }">
                          <v-icon v-bind="props" size="small" class="ml-1">
                            help_outline
                          </v-icon>
                        </template>
                        Ejemplo: anden línea 7 dirección barranca
                      </v-tooltip>
                    </label>

                    <div class="mb-2">
                      <label class="text-caption text-medium-emphasis">
                        Origen (de dónde parte)
                      </label>
                      <v-text-field
                        v-model="stair.connectionPoints.pointA"
                        variant="outlined"
                        density="compact"
                        placeholder="Ej: Anden dirección barranca"
                        hide-details
                      ></v-text-field>
                    </div>

                    <div>
                      <label class="text-caption text-medium-emphasis">
                        Destino (a dónde llega)
                      </label>
                      <v-text-field
                        v-model="stair.connectionPoints.pointB"
                        variant="outlined"
                        density="compact"
                        placeholder="Ej: Vestíbulo principal"
                        hide-details
                      ></v-text-field>
                    </div>
                  </div>

                  <!-- Detalles -->
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">
                      Describe detalles para identificar la escalera
                    </label>
                    <v-textarea
                      v-model="stair.details"
                      variant="outlined"
                      rows="2"
                      auto-grow
                      placeholder="Detalles adicionales..."
                      hide-details
                      density="compact"
                    ></v-textarea>
                  </div>

                  <!-- ¿Funciona? -->
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">
                      ¿Funciona la escalera?
                    </label>
                    <v-radio-group
                      v-model="stair.isWorking"
                      inline
                      hide-details
                    >
                      <v-radio
                        label="Sí"
                        :value="true"
                        color="success"
                        class="mr-3"
                      ></v-radio>
                      <v-radio label="No" :value="false" color="error">
                      </v-radio>
                    </v-radio-group>
                  </div>

                  <!-- Fotos -->
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">
                      Adjunta fotos de la escalera y sus identificadores
                    </label>
                    <UploadImage
                      :title="'Subir fotos'"
                      :typeFiles="'image/*'"
                      :stairId="index"
                    />
                  </div>

                  <!-- Botón confirmar escalera -->
                  <v-btn
                    color="primary"
                    block
                    @click="markStairComplete(index)"
                    :variant="
                      stair.status === 'completed' ? 'outlined' : 'elevated'
                    "
                  >
                    <v-icon start>
                      {{
                        stair.status === "completed" ? "check_circle" : "check"
                      }}
                    </v-icon>
                    {{
                      stair.status === "completed"
                        ? "Completada"
                        : "Completar escalera"
                    }}
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>

        <!-- Botón guardar todo -->
        <v-card class="rounded-0" _variant="flat" _color="primary">
          <v-card-actions class="pa-4">
            <v-btn
              color="primary"
              size="large"
              block
              variant="elevated"
              :disabled="surveyStore.completedStairs < surveyStore.totalStairs"
              @click="handleSave"
            >
              Guardar datos
              <v-icon end>save</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.gap-2 {
  gap: 8px;
}

label {
  font-weight: 500;
}
</style>

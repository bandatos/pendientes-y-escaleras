<script setup>
import { ref, computed } from 'vue'
import { useSurveyStore } from '../stores/surveyStore'
import { useStationStore } from '../stores/stationStore'
import { useSyncStore } from '../stores/syncStore'
import { useImageStore } from '../stores/imageStore'
import { useSnackbarStore } from '../stores/snackbarStore'
import { IndexedDBService } from '../services/indexDB.js'
import UploadImage from '../components/UploadImage.vue'
import Stats from "@/components/form/Stats.vue";
import StairForm from "@/components/form/StairForm.vue";

const emit = defineEmits(['save-complete', 'back'])

// Stores
const surveyStore = useSurveyStore()
const stationStore = useStationStore()
const syncStore = useSyncStore()
const imageStore = useImageStore()
const snackbarStore = useSnackbarStore()

const { currentSurvey } = surveyStore
const { selectedStation } = stationStore

// Estado local
const expandedPanels = ref([])
const newCodes = ref({}) // Códigos temporales por escalera

// Computed
const connectionStatus = computed(() =>
  syncStore.isOnline ? '🟢 Conectado' : '🔴 Sin conexión'
)

const pendingCount = computed(() => syncStore.syncStats.pending)


const all_status = [
  { label: 'Pendiente', icon: 'circle', color: 'grey', key: 'pending' },
  { label: 'Funciona', icon: 'check_circle', color: 'green', is_working: true, },
  { label: 'No funciona', icon: 'cancel', color: 'red', },
]

// Obtener icono del estado
const getStairStatusIcon = (stair) => {
  if (stair.status === 'pending') return 'circle'
  return stair.is_working ? 'check_circle' : 'cancel'
}

// Agregar código de identificación
const addCode = (stairIndex) => {
  const code = newCodes.value[stairIndex]
  if (code?.trim()) {
    if (!surveyStore.currentSurvey.stairs[stairIndex].code_identifiers) {
      surveyStore.currentSurvey.stairs[stairIndex].code_identifiers = []
    }
    surveyStore.currentSurvey.stairs[stairIndex].code_identifiers.push(
      code.trim())
    newCodes.value[stairIndex] = ''
  }
}

// Remover código
const removeCode = (stairIndex, codeIndex) => {
  surveyStore.currentSurvey.stairs[stairIndex].code_identifiers.splice(
    codeIndex, 1)
}

// Marcar escalera como completada
const markStairComplete = (stairIndex) => {
  const stair = surveyStore.currentSurvey.stairs[stairIndex]

  // Validaciones básicas
  // Solo validar códigos si hasCodes no está explícitamente marcado como true (sin códigos)
  const hasNoCodes = stair.hasCodes === true
  const hasCodesEmpty = !stair.code_identifiers || stair.code_identifiers.length === 0

  if (!hasNoCodes && hasCodesEmpty) {
    snackbarStore.showWarning('Agrega al menos un código de identificación o marca que no hay códigos visibles')
    return
  }

  if (!stair.route_start?.trim()) {
    snackbarStore.showWarning('Especifica el punto de inicio')
    return
  }

  if (stair.is_working === null) {
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

  if (stairIndex < surveyStore.total_stairs - 1) {
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
    for (let stairIndex = 0; stairIndex < surveyStore.total_stairs; stairIndex++) {
      const photos = imageStore.getStairPhotos(stairIndex)

      if (photos && photos.length > 0) {
        await IndexedDBService.saveStairImages(
          savedRecord.id,
          stairIndex + 1, // number es 1-based
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
                  backgroundColor: selectedStation?.line_color || 'grey',
                  color: 'white',
                }"
                class="mr-2"
                size="small"
              >
                {{ selectedStation?.lines || selectedStation?.first_route?.route_short_name }}
              </v-chip>
              <h2 class="text-subtitle-1 font-weight-bold">
                Estación {{ selectedStation?.name }}
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

        <Stats
          :surveyStore="surveyStore"
          class="mb-2"
        />

        <v-divider></v-divider>
        <v-card-subtitle>
          Completa la info en el orden en el que recorras la estación
        </v-card-subtitle>

        <!-- Expansion Panels de Escaleras -->
        <v-expansion-panels v-model="expandedPanels" multiple>
          <StairForm
            v-for="(stair, index) in surveyStore.currentSurvey?.stairs"
            :key="index"
            :stair="stair"
            :stair_index="index"
            :all_status="all_status"
          />
        </v-expansion-panels>

        <!-- Botón guardar todo -->
        <v-card class="rounded-0" _variant="flat" _color="primary">
          <v-card-actions class="pa-4">
            <v-btn
              color="primary"
              size="large"
              block
              variant="elevated"
              :disabled="surveyStore.completedStairs < surveyStore.total_stairs"
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

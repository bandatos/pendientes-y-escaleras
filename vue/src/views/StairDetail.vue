<script setup>
import { ref, computed, watch } from 'vue'
import { useSurveyStore } from '../stores/surveyStore'
import UploadImage from '../components/UploadImage.vue'

const emit = defineEmits(['back-to-summary', 'stair-completed'])

// Stores
const surveyStore = useSurveyStore()

// Estado local del formulario
const formData = ref({
  identificationCodes: [],
  connectionPoints: {
    pointA: '',
    pointB: ''
  },
  details: '',
  isWorking: null,
  photos: []
})

// Código temporal para agregar
const newCode = ref('')

// Watch para cargar datos de escalera actual
watch(() => surveyStore.currentStair, (stair) => {
  if (stair) {
    formData.value = {
      identificationCodes: [...(stair.identificationCodes || [])],
      connectionPoints: { ...stair.connectionPoints },
      details: stair.details || '',
      isWorking: stair.isWorking,
      photos: []
    }
  }
}, { immediate: true })

// Computed
const stairNumber = computed(() => surveyStore.currentStair?.stairNumber || 0)

const canGoNext = computed(() => !surveyStore.isLastStair)

const canGoPrevious = computed(() => surveyStore.currentStairIndex > 0)

// Agregar código de identificación
const addIdentificationCode = () => {
  if (newCode.value.trim()) {
    formData.value.identificationCodes.push(newCode.value.trim())
    newCode.value = ''
  }
}

// Remover código
const removeCode = (index) => {
  formData.value.identificationCodes.splice(index, 1)
}

// Validar formulario
const validateForm = () => {
  const errors = []

  if (formData.value.identificationCodes.length === 0) {
    errors.push('Debe tener al menos un código de identificación')
  }

  if (!formData.value.connectionPoints.pointA.trim()) {
    errors.push('Debe especificar el punto A de conexión')
  }

  if (formData.value.isWorking === null) {
    errors.push('Debe indicar si la escalera funciona')
  }

  return errors
}

// Guardar y continuar
const handleSaveAndNext = async () => {
  const errors = validateForm()

  if (errors.length > 0) {
    alert('⚠️ Faltan datos:\n' + errors.join('\n'))
    return
  }

  try {
    // Actualizar datos de escalera actual
    surveyStore.updateCurrentStair({
      identificationCodes: formData.value.identificationCodes,
      connectionPoints: formData.value.connectionPoints,
      details: formData.value.details,
      isWorking: formData.value.isWorking
    })

    emit('stair-completed')

    // Si hay siguiente, avanzar
    if (canGoNext.value) {
      surveyStore.nextStair()
    } else {
      // Última escalera, volver al summary
      emit('back-to-summary')
    }

  } catch (error) {
    console.error('Error guardando escalera:', error)
    alert('❌ Error al guardar')
  }
}

// Volver a escalera anterior
const handlePrevious = () => {
  surveyStore.previousStair()
}

// Cerrar sin guardar
const handleClose = () => {
  if (confirm('¿Salir sin guardar los cambios?')) {
    emit('back-to-summary')
  }
}
</script>

<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" class="fill-height">
      <v-col cols="12" sm="10" md="8" lg="6">

        <!-- Header -->
        <v-card class="mb-4" variant="outlined">
          <v-card-text class="d-flex align-center">
            <v-select
              :model-value="surveyStore.currentStairIndex"
              :items="Array.from({ length: surveyStore.totalStairs }, (_, i) => ({
                title: `Escalera ${i + 1}`,
                value: i
              }))"
              @update:model-value="surveyStore.goToStair($event)"
              variant="outlined"
              density="compact"
              hide-details
              style="max-width: 200px"
            ></v-select>

            <v-spacer></v-spacer>

            <v-btn
              icon="mdi-close"
              size="small"
              variant="text"
              @click="handleClose"
            ></v-btn>
          </v-card-text>
        </v-card>

        <!-- Formulario -->
        <v-card elevation="2">
          <v-card-text>

            <!-- Nota informativa -->
            <v-alert
              type="info"
              variant="tonal"
              density="compact"
              class="mb-4"
            >
              A veces las escaleras tienen varios códigos o identificadores
            </v-alert>

            <!-- Códigos de identificación -->
            <div class="mb-4">
              <label class="text-subtitle-2 mb-2 d-block">
                Escribe todos los códigos de identificación que tenga la escalera
                <v-tooltip location="top">
                  <template v-slot:activator="{ props }">
                    <v-icon
                      v-bind="props"
                      size="small"
                      class="ml-1"
                    >mdi-help-circle-outline</v-icon>
                  </template>
                  Por ejemplo: KSG3-43, ALT-01, etc.
                </v-tooltip>
              </label>

              <!-- Input para agregar código -->
              <div class="d-flex gap-2 mb-2">
                <v-text-field
                  v-model="newCode"
                  variant="outlined"
                  density="comfortable"
                  placeholder="Ej: KSG3-43"
                  hide-details
                  @keyup.enter="addIdentificationCode"
                ></v-text-field>
                <v-btn
                  icon="mdi-plus"
                  color="primary"
                  @click="addIdentificationCode"
                ></v-btn>
              </div>

              <!-- Lista de códigos -->
              <div class="d-flex flex-wrap gap-2">
                <v-chip
                  v-for="(code, index) in formData.identificationCodes"
                  :key="index"
                  closable
                  @click:close="removeCode(index)"
                  color="primary"
                  variant="outlined"
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
                    <v-icon
                      v-bind="props"
                      size="small"
                      class="ml-1"
                    >mdi-help-circle-outline</v-icon>
                  </template>
                  Por ejemplo: anden línea 7 dirección barranca
                </v-tooltip>
              </label>

              <div class="mb-3">
                <label class="text-caption text-medium-emphasis">Punto A</label>
                <v-text-field
                  v-model="formData.connectionPoints.pointA"
                  variant="outlined"
                  density="comfortable"
                  placeholder="Ej: Anden dirección barranca"
                  hide-details
                ></v-text-field>
              </div>

              <div>
                <label class="text-caption text-medium-emphasis">Punto B</label>
                <v-text-field
                  v-model="formData.connectionPoints.pointB"
                  variant="outlined"
                  density="comfortable"
                  placeholder="Ej: Vestíbulo principal"
                  hide-details
                ></v-text-field>
              </div>
            </div>

            <!-- Detalles adicionales -->
            <div class="mb-4">
              <label class="text-subtitle-2 mb-2 d-block">
                Describe detalles para identificar la escalera
                <v-tooltip location="top">
                  <template v-slot:activator="{ props }">
                    <v-icon
                      v-bind="props"
                      size="small"
                      class="ml-1"
                    >mdi-help-circle-outline</v-icon>
                  </template>
                  Por ejemplo, si hay dos escaleras juntas, una es izquierda
                  y la otra derecha (bajando desde abajo). O extremo izquierdo, etc.
                </v-tooltip>
              </label>

              <v-textarea
                v-model="formData.details"
                variant="outlined"
                rows="3"
                placeholder="Detalles adicionales..."
                hide-details
              ></v-textarea>
            </div>

            <!-- ¿Funciona? -->
            <div class="mb-4">
              <label class="text-subtitle-2 mb-2 d-block">¿Funciona?</label>
              <v-radio-group
                v-model="formData.isWorking"
                inline
                hide-details
              >
                <v-radio label="Sí" :value="true"></v-radio>
                <v-radio label="No" :value="false"></v-radio>
              </v-radio-group>
            </div>

            <!-- Fotos -->
            <div class="mb-4">
              <label class="text-subtitle-2 mb-2 d-block">
                Adjunta hasta 3 fotos de la escalera y sus identificadores
              </label>

              <UploadImage
                :title="'Subir fotos'"
                :typeFiles="'image/*'"
              />
            </div>

          </v-card-text>

          <!-- Acciones -->
          <v-card-actions class="pa-4">
            <v-btn
              variant="outlined"
              @click="handleClose"
            >
              Cerrar
            </v-btn>

            <v-spacer></v-spacer>

            <v-btn
              v-if="canGoPrevious"
              variant="text"
              @click="handlePrevious"
            >
              <v-icon start>mdi-chevron-left</v-icon>
              Anterior
            </v-btn>

            <v-btn
              color="primary"
              @click="handleSaveAndNext"
            >
              {{ canGoNext ? 'Siguiente' : 'Terminar' }}
              <v-icon end>{{ canGoNext ? 'mdi-chevron-right' : 'mdi-check' }}</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- Info de progreso -->
        <v-card class="mt-4" variant="outlined">
          <v-card-text class="text-caption text-center">
            Escalera {{ stairNumber }} de {{ surveyStore.totalStairs }}
            <v-progress-linear
              :model-value="surveyStore.progress"
              color="primary"
              class="mt-2"
              height="4"
              rounded
            ></v-progress-linear>
          </v-card-text>
        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
label {
  font-weight: 500;
}

.gap-2 {
  gap: 8px;
}
</style>

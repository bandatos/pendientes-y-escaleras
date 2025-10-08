<script setup>
import { ref, onMounted, computed } from 'vue'
import { useStationStore } from '../stores/stationStore'
import { useSurveyStore } from '../stores/surveyStore'
import { useSyncStore } from '../stores/syncStore'

const emit = defineEmits(['station-selected'])

// Stores
const stationStore = useStationStore()
const surveyStore = useSurveyStore()
const syncStore = useSyncStore()

// Estado local
const selectedStationId = ref(null)

// Computed
const connectionStatus = computed(() =>
  syncStore.isOnline ? '🟢 Conectado' : '🔴 Sin conexión'
)

const pendingCount = computed(() => syncStore.syncStats.pending)

// Inicializar
onMounted(async () => {
  await stationStore.init()
  await syncStore.init()
})

// Manejar selección de estación
const handleSelectStation = () => {
  if (!selectedStationId.value) {
    alert('Por favor selecciona una estación')
    return
  }

  // Buscar estación completa
  const station = stationStore.stationsCatalog.find(
    s => s.stationId === selectedStationId.value
  )

  if (station) {
    // Seleccionar en store
    stationStore.selectStation(station)

    // Iniciar relevamiento
    surveyStore.startSurvey(station)

    // Emitir evento para cambiar de vista
    emit('station-selected', station)
  }
}
</script>

<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" sm="10" md="8" lg="6">

        <!-- Status bar -->
        <v-card class="mb-4 pa-2" variant="outlined">
          <div class="d-flex justify-space-between align-center">
            <span class="text-body-2">{{ connectionStatus }}</span>
            <span v-if="pendingCount > 0" class="text-warning text-body-2">
              📋 {{ pendingCount }} pendientes
            </span>
          </div>
        </v-card>

        <!-- Título principal -->
        <div class="text-center mb-6">
          <h1 class="text-h4 mb-2">Relevamiento de Escaleras</h1>
          <p class="text-subtitle-1 text-medium-emphasis">
            Elige la estación en la que te encuentras
          </p>
        </div>

        <!-- Selector de estación -->
        <v-card elevation="2">
          <v-card-text>
            <v-autocomplete
              v-model="selectedStationId"
              :items="stationStore.stationsCatalog"
              item-title="name"
              item-value="stationId"
              label="Selecciona una estación"
              variant="outlined"
              clearable
              :loading="stationStore.isLoading"
            >
              <template v-slot:chip="{ props, item }">
                <v-chip
                  v-bind="props"
                  :style="{ backgroundColor: item.raw.lineColor, color: 'white' }"
                >
                  {{ item.raw.name }}
                </v-chip>
              </template>

              <template v-slot:item="{ props, item }">
                <v-list-item
                  v-bind="props"
                  :title="item.raw.name"
                  :subtitle="`${item.raw.line} • ${item.raw.totalStairs} escaleras`"
                >
                  <template v-slot:prepend>
                    <v-avatar
                      :style="{ backgroundColor: item.raw.lineColor }"
                      size="40"
                    >
                      <span class="text-white text-caption">
                        {{ item.raw.line.replace('Línea ', '') }}
                      </span>
                    </v-avatar>
                  </template>
                </v-list-item>
              </template>
            </v-autocomplete>

            <!-- Placeholder del mapa -->
            <div class="map-placeholder mt-4">
              <v-card
                variant="tonal"
                color="grey-lighten-3"
                height="300"
                class="d-flex align-center justify-center"
              >
                <div class="text-center">
                  <v-icon size="64" color="grey">mdi-map-outline</v-icon>
                  <p class="text-body-2 text-medium-emphasis mt-2">
                    Mapa del metro
                  </p>
                  <p class="text-caption text-disabled">
                    (Próximamente)
                  </p>
                </div>
              </v-card>
            </div>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              size="large"
              :disabled="!selectedStationId"
              @click="handleSelectStation"
              block
            >
              Continuar
              <v-icon end>mdi-arrow-right</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- Info adicional -->
        <v-card class="mt-4" variant="outlined">
          <v-card-text class="text-caption text-center">
            <v-icon size="small" class="mb-1">mdi-information-outline</v-icon>
            Selecciona la estación donde realizarás el relevamiento de escaleras
          </v-card-text>
        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.map-placeholder {
  border-radius: 8px;
  overflow: hidden;
}

h1 {
  font-weight: 500;
}
</style>

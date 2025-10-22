<script setup>
import { ref, onMounted, computed } from 'vue'
import { useStationStore } from '../stores/stationStore'
import { useSurveyStore } from '../stores/surveyStore'
import { useSyncStore } from '../stores/syncStore'
import { useSnackbarStore } from '../stores/snackbarStore'
import MapaMetro from '../components/vis/MapaMetro.vue'
import AvatarStation from "@/components/select_station/AvatarStation.vue";

const emit = defineEmits(['station-selected'])

// Stores
const stationStore = useStationStore()
const surveyStore = useSurveyStore()
const syncStore = useSyncStore()
const snackbarStore = useSnackbarStore()

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
  console.log('Estación seleccionada:', selectedStationId.value)
  if (!selectedStationId.value) {
    snackbarStore.showWarning('Por favor selecciona una estación')
    return
  }

  // Buscar estación completa
  const station = stationStore.stationsCatalog.find(
    s => s.station_id === selectedStationId.value
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
  <v-container fluid class="fill-height pt-0">
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" sm="10" md="8" lg="6" class="pt-0">

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
          <h1 class="text-h5 text-sm-h4 mb-2">Relevamiento de Escaleras</h1>
          <p v-if="false" class="text-subtitle-1 text-medium-emphasis">
            Elige la estación en la que te encuentras
          </p>
        </div>

        <!-- Selector de estación -->
        <v-card elevation="2" class="mb-4">
          <v-card-text>
            <v-autocomplete
              v-model="selectedStationId"
              :items="stationStore.stationsCatalog"
              item-title="name"
              item-value="station_id"
              label="Escribe/Selecciona una estación"
              variant="outlined"
              hide-details
              :loading="stationStore.isLoading"
              @update:modelValue="handleSelectStation"
            >
              <template v-slot:chip="{ props, item }">
                <v-chip
                  v-bind="props"
                  :style="{ backgroundColor: item.raw.line_color, color: 'white' }"
                >
                  {{ item.raw.name }}
                </v-chip>
              </template>

              <template v-slot:item="{ props, item }">
                <v-list-item
                  v-bind="props"
                  :title="item.raw.name"
                  :subtitle="`${item.raw.line} • ${item.raw.total_stairs} escaleras`"
                >
                  <template v-slot:prepend>
                    <v-avatar
                      v-if="false"
                      :style="{ backgroundColor: item.raw.line_color }"
                      size="40"
                    >
                      <span class="text-white text-caption">
                        {{ item.raw.line.replace('Línea ', '') }}
                      </span>
                    </v-avatar>
                    <!-- RICK: Esto de las franjas es solo experimental -->
                    <AvatarStation
                      :colors="[item.raw.line_color, '#164ec9']"
                      :line_text="item.raw.line.replace('Línea ', '')"
                    />


                  </template>
                </v-list-item>
              </template>
            </v-autocomplete>

          </v-card-text>

<!--          Comento esto porque me parece que con elegirla es suficiente-->
<!--          <v-card-actions>-->
<!--            <v-spacer></v-spacer>-->
<!--            <v-btn-->
<!--              color="primary"-->
<!--              size="large"-->
<!--              :disabled="!selectedStationId"-->
<!--              @click="handleSelectStation"-->
<!--              block-->
<!--            >-->
<!--              Comenzar-->
<!--              <v-icon end>keyboard_arrow_right</v-icon>-->
<!--            </v-btn>-->
<!--          </v-card-actions>-->
        </v-card>
        <v-card>
            <!-- Mapa del metro -->
            <div class="map-container mt-4">
              <MapaMetro />
            </div>

        </v-card>

        <!-- Info adicional -->
        <v-card class="mt-4" variant="outlined">
          <v-card-text class="text-caption text-center">
            <v-icon size="small" class="mb-1">info</v-icon>
            Selecciona la estación donde realizarás el relevamiento de escaleras
          </v-card-text>
        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.map-container {
  border-radius: 8px;
  overflow: hidden;
}

h1 {
  font-weight: 500;
}
</style>

<script setup>
import { ref, onMounted } from 'vue'

// Extra Stores
import { useStationStore } from '../stores/stationStore'
import { useSurveyStore } from '../stores/surveyStore'
import { useSyncStore } from '../stores/syncStore'
import { useSnackbarStore } from '../stores/snackbarStore'
import { useAuthStore } from '../stores/authStore'

// Extra Components
import MapaMetro from '../components/vis/MapaMetro.vue'
import AvatarStation from "@/components/select_station/AvatarStation.vue"
import LoginDialog from "@/components/LoginDialog.vue"

const emit = defineEmits(['station-selected'])

// Stores
const stationStore = useStationStore()
const surveyStore = useSurveyStore()
const syncStore = useSyncStore()
const snackbarStore = useSnackbarStore()
const authStore = useAuthStore()

// Estado local
const selectedStationId = ref(null)
const showLoginDialog = ref(false)
const pendingStation = ref(null)

onMounted(async () => {
  // Iniciando los stores.
  await stationStore.init()
  await syncStore.init()
})

const handleSelectStation = () => {
  console.log('Estación seleccionada:', selectedStationId.value)
  if (!selectedStationId.value) {
    snackbarStore.showWarning('Por favor selecciona una estación')
    return
  }

  // Buscar estación completa
  const station = stationStore.fullStations.find(
    s => s.id === selectedStationId.value)
  if (station.total_stairs === 0) {
    snackbarStore.showWarning(
      'La estación seleccionada no tiene escaleras para relevar \n ' +
      'Por favor elige otra estación')
    selectedStationId.value = null
    return
  }

  if (!station)
    return

  // Verificar autenticación
  if (!authStore.isAuthenticated) {
    // Guardar estación pendiente y mostrar diálogo de login
    pendingStation.value = station
    showLoginDialog.value = true
    return
  }

  // Si está autenticado, continuar con el flujo normal
  proceedWithStation(station)
}

const proceedWithStation = (station) => {
  // Seleccionar en store
  stationStore.selectStation(station)

  // Iniciar relevamiento
  surveyStore.startSurvey(station)

  // Emitir evento para cambiar de vista
  emit('station-selected', station)
}

const handleLoginSuccess = () => {
  // Una vez autenticado, proceder con la estación pendiente
  if (pendingStation.value) {
    proceedWithStation(pendingStation.value)
    pendingStation.value = null
  }
}

const handleLoginCancel = () => {
  // Limpiar selección si cancela el login
  selectedStationId.value = null
  pendingStation.value = null
}
</script>

<template>
  <v-row justify="center" class="fill-height mt-10">
    <v-col cols="12" sm="10" md="8" lg="6" class="pt-0">

      <!-- Login Dialog -->
      <LoginDialog
        v-model="showLoginDialog"
        :station-name="pendingStation?.name || ''"
        @login-success="handleLoginSuccess"
        @login-cancel="handleLoginCancel"
      />

      <!-- Título principal -->
      <div class="text-center mb-6">
        <h1 class="text-h5 text-sm-h4 mb-2">
          Pendientes y Escaleras
        </h1>
        <span class="text-body-1 text-medium-emphasis">
          Relevamiento de escaleras eléctricas en el Metro de la Ciudad de México
        </span>
        <p v-if="false" class="text-subtitle-1 text-medium-emphasis">
          Elige la estación en la que te encuentras
        </p>
      </div>

      <!-- Selector de estación -->
      <v-card elevation="2" class="mb-4">
        <v-card-text>

          <v-autocomplete
            v-model="selectedStationId"
            :items="stationStore.fullStations"
            item-title="name"
            item-value="id"
            label="Escribe/Selecciona una estación"
            variant="outlined"
            hide-details
            :loading="stationStore.isLoading"
            @update:modelValue="handleSelectStation"

          >
            <template v-slot:chip="{ props, item }">
              <v-chip
                v-bind="props"
                :style="{ backgroundColor: item.raw.first_route.line_color, color: 'white' }"
              >
                {{ item.raw.name }}
              </v-chip>
            </template>

            <template v-slot:item="{ props, item }">
              <v-list-item
                v-bind="props"
                :diabled="!item.raw.total_stairs"
              >
                <template v-slot:title>
                  <span class="text-body-1 font-weight-medium">
                    {{ item.raw.name }}
                  </span>
                </template>
                <template v-slot:subtitle>
                  {{ item.raw.lines_text || item.raw.first_route.route_desc || 'Línea ??' }}
                  • {{ item.raw.total_stairs }}
                  escalera{{ item.raw.total_stairs === 1 ? '' : 's' }}
                </template>
                <template v-slot:prepend>
                  <AvatarStation :station-data="item.raw" />
                </template>
              </v-list-item>
            </template>
          </v-autocomplete>

        </v-card-text>
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
</template>

<style lang="scss">
.map-container {
  border-radius: 8px;
  overflow: hidden;
}

h1 {
  font-weight: 500;
}


</style>

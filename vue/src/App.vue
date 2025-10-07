<script setup>
import { ref } from 'vue'
import StationSelector from './views/StationSelector.vue'
import StationSummary from './views/StationSummary.vue'

// Estado de navegación
const currentView = ref('selector') // 'selector' | 'summary'

// Navegar entre vistas
const goToSummary = () => {
  currentView.value = 'summary'
}

const goToSelector = () => {
  currentView.value = 'selector'
}

// Handlers de eventos
const handleStationSelected = () => {
  goToSummary()
}

const handleSaveComplete = () => {
  // Relevamiento completo guardado
  alert('✅ Relevamiento guardado exitosamente')
  goToSelector()
}

const handleBack = () => {
  goToSelector()
}
</script>

<template>
  <v-app>
    <!-- Vista 1: Selector de Estación -->
    <StationSelector
      v-if="currentView === 'selector'"
      @station-selected="handleStationSelected"
    />

    <!-- Vista 2: Resumen de Escaleras (con expansion panels) -->
    <StationSummary
      v-else-if="currentView === 'summary'"
      @save-complete="handleSaveComplete"
      @back="handleBack"
    />
  </v-app>
</template>

<style scoped>
/* Global app styles */
</style>
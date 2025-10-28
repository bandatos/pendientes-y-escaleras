<script setup>
import { ref, onMounted } from "vue";
import StationSelector from "./views/StationSelector.vue";
import StationSummary from "./views/StationSummary.vue";
import MessageSnackBar from "./components/MessageSnackBar.vue";
import { useSnackbarStore } from "./stores/snackbarStore";
import { useAuthStore } from "./stores/authStore";

import SyncStatusBar from "@/components/SyncStatusBar.vue"

const snackbarStore = useSnackbarStore();
const authStore = useAuthStore();

// Cargar sesión al iniciar la aplicación
onMounted(() => {
  console.log('🚀 App iniciada - verificando sesión guardada...');
  authStore.loadSession();
});

// Estado de navegación
const currentView = ref("selector"); // 'selector' | 'summary'

// Navegar entre vistas
const goToSummary = () => {
  currentView.value = "summary";
};

const goToSelector = () => {
  currentView.value = "selector";
};

// Handlers de eventos
const handleStationSelected = () => {
  console.log("Navegando a resumen de estación");
  goToSummary();
};

const handleSaveComplete = () => {
  // Relevamiento completo guardado
  snackbarStore.showSuccess("Relevamiento guardado exitosamente");
  goToSelector();
};

const handleBack = () => {
  goToSelector();
};
</script>

<template>
  <v-app>
    <v-main>
      <v-container
        class="px-2 pt-0 fill-height"
        fluid
        max-width="1440"
      >
        <SyncStatusBar :show-sync-button="true" class="mt-2 w-100"/>


        <!-- Vista 1: Vista General -->
        <StationSelector
          v-if="currentView === 'selector'"
          @station-selected="handleStationSelected"
        />

        <!-- Vista 2: Form Station -->
        <StationSummary
          v-else-if="currentView === 'summary'"
          @save-complete="handleSaveComplete"
          @back="handleBack"
        />

        <!-- Snackbar global -->
        <MessageSnackBar />
      </v-container>
    </v-main>
  </v-app>
</template>

<style lang="scss">

.stripe-square {
  height: 40px;
  width: 40px;
  border-radius: 0 16px 0 0 !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
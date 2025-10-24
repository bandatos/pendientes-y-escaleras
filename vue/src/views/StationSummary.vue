<script setup>
import { ref, computed, onMounted } from "vue";
import { useSurveyStore } from "../stores/surveyStore";
import { useStationStore } from "../stores/stationStore";
import { useSyncStore } from "../stores/syncStore";
import { useImageStore } from "../stores/imageStore";
import { useSnackbarStore } from "../stores/snackbarStore";
import { useAuthStore } from "../stores/authStore";
import { IndexedDBService } from "../services/indexDB.js";
import UploadImage from "../components/UploadImage.vue";
import Stats from "@/components/form/Stats.vue";
import StairForm from "@/components/form/StairForm.vue";
import AvatarStation from "@/components/select_station/AvatarStation.vue";
import SyncStatusBar from "@/components/SyncStatusBar.vue";

const emit = defineEmits(["save-complete", "back"]);

// Stores
const surveyStore = useSurveyStore();
const stationStore = useStationStore();
const syncStore = useSyncStore();
const imageStore = useImageStore();
const snackbarStore = useSnackbarStore();
const authStore = useAuthStore();

// Actualizar estadísticas de sincronización al montar
onMounted(async () => {
  // Cargar sesión si existe
  authStore.loadSession();

  // Validar autenticación
  if (!authStore.isAuthenticated) {
    snackbarStore.showError('Debes autenticarte para realizar relevamientos');
    emit('back');
    return;
  }

  await syncStore.updateSyncStats();
});

const { currentSurvey, currentStairs } = surveyStore;
const { selectedStation } = stationStore;

// Estado local
const expandedPanels = ref([]);

const all_status = [
  { label: "Pendiente", icon: "circle", color: "grey", key: "pending" },
  { label: "Funciona", icon: "check_circle", color: "green", is_working: true },
  { label: "No funciona", icon: "cancel", color: "red" },
];

// Marcar escalera como completada
const markStairComplete = (stairIndex) => {
  // Cerrar panel actual y abrir siguiente (si existe)
  const currentIndex = expandedPanels.value.indexOf(stairIndex);
  if (currentIndex > -1) {
    expandedPanels.value.splice(currentIndex, 1);
  }

  if (stairIndex < surveyStore.total_stairs - 1) {
    expandedPanels.value.push(stairIndex + 1);
  }
};

function showWarning(message) {
  snackbarStore.showWarning(message);
}

// Guardar datos completos
const handleSave = async () => {
  try {
    // Validar que todas las escaleras estén completadas
    const allCompleted = currentStairs.every((s) => s.status === "completed");

    if (!allCompleted) {
      snackbarStore.showWarning(
        "Debes completar todas las escaleras antes de guardar"
      );
      return;
    }

    // 1. Guardar registro de estación en IndexedDB
    const savedRecord = await surveyStore.completeSurvey();

    // 2. Guardar imágenes de cada escalera
    for (
      let stairIndex = 0;
      stairIndex < surveyStore.total_stairs;
      stairIndex++
    ) {
      const photos = imageStore.getStairPhotos(stairIndex);

      if (photos && photos.length > 0) {
        await IndexedDBService.saveStairImages(
          savedRecord.id,
          stairIndex + 1, // number es 1-based
          photos
        );
        console.log(`📸 ${photos.length}
          imágenes guardadas para escalera ${stairIndex + 1}`);
      }
    }

    // 3. Limpiar el imageStore
    imageStore.clearSelection();

    // 4. Actualizar estadísticas de sincronización
    await syncStore.updateSyncStats();

    console.log("✅ Estación y todas las imágenes guardadas exitosamente");

    emit("save-complete");
  } catch (error) {
    console.error("Error guardando:", error);
    snackbarStore.showError("Error al guardar los datos");
  }
};

// Volver a selector
const handleBack = () => {
  if (
    confirm("¿Seguro que quieres salir? Se perderá el progreso no guardado")
  ) {
    surveyStore.cancelSurvey();
    emit("back");
  }
};
</script>

<template>
  <v-container fluid class="fill-height pa-0">
    <v-row no-gutters class="fill-height">
      <v-col cols="12">
        <!-- Header con status -->
        <v-card class="rounded-0" variant="flat" color="grey-lighten-5">
          <v-card-text>
            <!-- Status bar con botón de sincronización -->
            <SyncStatusBar :show-sync-button="true" variant="flat" class="pa-0 mb-2" />

            <!-- Estación seleccionada -->
            <div class="d-flex align-center">
              <AvatarStation :station-data="selectedStation" class="mr-3" />
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

        <Stats :surveyStore="surveyStore" class="mb-2" />

        <v-divider></v-divider>
        <v-card-subtitle>
          Completa la info en el orden en el que recorras la estación
        </v-card-subtitle>

        <!-- Expansion Panels de Escaleras -->
        <v-expansion-panels v-model="expandedPanels" multiple>
          <StairForm
            v-for="(stair, stair_index) in currentStairs"
            :key="stair.id"
            :stair="stair"
            :stair_index="stair_index"
            :all_status="all_status"
            @showWarning="showWarning"
            @markComplete="markStairComplete(stair_index)"
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

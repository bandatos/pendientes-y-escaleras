<script setup>
import { useSyncStore } from "../stores/syncStore";
import { useAuthStore } from "../stores/authStore";

const props = defineProps({
  showSyncButton: {
    type: Boolean,
    default: false,
  },
  variant: {
    type: String,
    default: "outlined", // 'outlined' | 'flat'
  },
});

const syncStore = useSyncStore();
const authStore = useAuthStore();

const connectionStatus = computed(() =>
  syncStore.isOnline ? "🟢 Conectado" : "🔴 Sin conexión"
);

const pendingCount = computed(() => syncStore.syncStats.pending);

const handleSync = async () => {
  try {
    await syncStore.forceSync();
  } catch (error) {
    console.error("Error durante sincronización manual:", error);
  }
};
</script>

<template>
  <v-card class="mb-4 pa-2" :variant="variant">
    <v-row align="center">
      <v-col cols="auto">
        <span class="text-body-2">{{ connectionStatus }}</span>
      </v-col>
      <v-col cols="auto" class="ml-n4">
        <v-btn
          v-if="showSyncButton && pendingCount > 0 && syncStore.isOnline"
          size="x-small"
          color="warning"
          variant="tonal"
          @click="handleSync"
          :loading="syncStore.isSyncing"
          prepend-icon="sync"
        >
          Sincronizar ({{ pendingCount }})
        </v-btn>
      </v-col>
      <v-spacer></v-spacer>
      <!-- Indicador de autenticación -->
      <v-col cols="auto">
        <v-chip
          v-if="authStore.isAuthenticated"
          color="success"
          variant="tonal"
          size="small"
          prepend-icon="check_circle"
        >
          {{ authStore.user?.email || "Autenticado" }}
        </v-chip>
      </v-col>
    </v-row>
  </v-card>
</template>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>

<script setup>
import { computed } from 'vue'
import { useSyncStore } from '../stores/syncStore'

const props = defineProps({
  showSyncButton: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'outlined' // 'outlined' | 'flat'
  }
})

const syncStore = useSyncStore()

const connectionStatus = computed(() =>
  syncStore.isOnline ? '🟢 Conectado' : '🔴 Sin conexión'
)

const pendingCount = computed(() => syncStore.syncStats.pending)

const handleSync = async () => {
  try {
    await syncStore.forceSync()
  } catch (error) {
    console.error('Error durante sincronización manual:', error)
  }
}
</script>

<template>
  <v-card class="mb-4 pa-2" :variant="variant">
    <div class="d-flex justify-space-between align-center">
      <div class="d-flex align-center gap-2">
        <span class="text-body-2">{{ connectionStatus }}</span>

        <!-- Botón de sincronización manual (solo si showSyncButton=true y hay pendientes) -->
        <v-btn
          v-if="showSyncButton && pendingCount > 0 && syncStore.isOnline"
          size="x-small"
          color="primary"
          variant="tonal"
          @click="handleSync"
          :loading="syncStore.isSyncing"
          prepend-icon="sync"
        >
          Sincronizar ({{ pendingCount }})
        </v-btn>
      </div>

      <span v-if="pendingCount > 0" class="text-warning text-body-2">
        📋 {{ pendingCount }} pendiente{{ pendingCount === 1 ? '' : 's' }}
      </span>
    </div>
  </v-card>
</template>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>

/**
 ** Store único para manejar el estado de sincronización de Pinia
 * Migrado de localStorage a IndexedDB
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
//Servicios propios:
import { IndexedDBService } from '../services/indexDB.js'
import { getApiSync } from '../services/apiSync.js'
import { getNetworkDetection } from '../services/networkDetection.js'
import { useSurveyStore } from './surveyStore.js'

export const useSyncStore = defineStore('sync', () => {
  // Estado reactivo                     ⬆️id único    
  const report = ref({
    line: null,
    station: "",
    typeElevation: "",
    is_working: true,
    evidenceImage: null,
    notes: "",
    date: new Date(),
  });

  const isOnline = ref(navigator.onLine)
  const isSyncing = ref(false)
  // Valores que tenemos para saber el estado.
  const syncStats = ref({
    total: 0, 
    synced: 0,
    pending: 0
  })
  const lastSyncTime = ref(null)
  const syncHistory = ref([])
  
/* Aquí en CompositionAPI a diferencia de optionsAPI, tenemos los servicios aparte, los
  envolvemos dentro de una const, para poder llamar a sus métodos */

  // Servicios
  const apiSync = getApiSync()
  let networkDetection = null;



  // Computed properties (getters)
  const syncProgress = computed(() => {
    if (syncStats.value.total === 0) return 100
    return Math.round((syncStats.value.synced / syncStats.value.total) * 100)
  })

  const hasPendingData = computed(() => syncStats.value.pending > 0)

  // Inicializar store
  async function init() {
    if (!networkDetection) {
      networkDetection = getNetworkDetection()
      // Listener para cambios de conectividad con auto-sync
      networkDetection.addListener(async (online) => {
        isOnline.value = online
        if (online) {
          console.log('🟢 Store: Conexión restaurada - iniciando auto-sync')
          // Auto-sync cuando se restaura la conexión
          setTimeout(async () => {
            await syncPendingData()
          }, 2000) // Dos segundo de tiempo para checar sincronización.
        } else {
          console.log('🔴 Store: Conexión perdida')
        }
      })
  
      // Actualizar stats iniciales
      await updateSyncStats()
  
      console.log('🏪 SyncStore inicializado')
    }
  }

  // Actualizar estadísticas de sync
  async function updateSyncStats() {
    const surveyStore = useSurveyStore()
    const stats = await surveyStore.getSyncStats()
    syncStats.value = stats
  }

  // Guardar datos del formulario
  async function saveFormData(formData) {
    try {
      console.log('💾 Store: Guardando datos del formulario en IndexedDB')

      // Guardar en IndexedDB (ahora es async)
      const savedData = await IndexedDBService.saveFormData(formData)

      // Actualizar estadísticas
      await updateSyncStats()

      // Intentar sync inmediato si hay conexión
      if (isOnline.value) {
        console.log('🔄 Store: Intentando sync inmediato')
        syncPendingData()
      } else {
        console.log('⏸️ Store: Sin conexión - datos guardados localmente en IndexedDB')
      }

      return savedData
    } catch (error) {
      console.error('❌ Store: Error guardando datos:', error)
      throw error
    }
  }

  // Sincronizar datos pendientes (escaleras)
  async function syncPendingData() {
    if (isSyncing.value) {
      console.log('⏳ SyncStore: Sync ya en progreso')
      return
    }

    try {
      isSyncing.value = true
      console.log('🔄 SyncStore: Iniciando sincronización de escaleras')

      const surveyStore = useSurveyStore()
      const result = await surveyStore.syncPendingStairs()

      // Actualizar estadísticas
      await updateSyncStats()

      // Actualizar historial
      if (result.synced > 0 || result.failed > 0) {
        addToSyncHistory({
          timestamp: Date.now(),
          synced: result.synced,
          failed: result.failed,
          success: result.failed === 0
        })

        lastSyncTime.value = Date.now()
      }

      console.log(`✅ SyncStore: Sync completo - ${result.synced} exitosos, ${result.failed} fallidos`)
      return result

    } catch (error) {
      console.error('❌ SyncStore: Error durante sync:', error)
      throw error
    } finally {
      isSyncing.value = false
    }
  }

  // Agregar entrada al historial de sync
  function addToSyncHistory(entry) {
    syncHistory.value.unshift(entry)
    
    // Mantener solo los últimos 10 registros
    if (syncHistory.value.length > 10) {
      syncHistory.value = syncHistory.value.slice(0, 10)
    }
  }

  // Obtener todos los datos guardados
  async function getAllSavedData() {
    return await IndexedDBService.getAllFormData()
  }

  // Obtener datos no sincronizados
  async function getUnsyncedData() {
    return await IndexedDBService.getUnsyncedData()
  }

  // Forzar sincronización manual
  async function forceSync() {
    console.log('🔄 Store: Forzando sync manual')
    return await syncPendingData()
  }

  // Limpiar datos antiguos
  async function cleanOldData() {
    await IndexedDBService.cleanOldData()
    await updateSyncStats()
    console.log('🧹 Store: Datos antiguos limpiados')
  }

  return {
    // State
    report,
    isOnline,
    isSyncing,
    syncStats,
    lastSyncTime,
    syncHistory,

    
    // Computed or getters
    syncProgress,
    hasPendingData,
    
    // Actions
    init,
    saveFormData,
    syncPendingData,
    forceSync,
    getAllSavedData,
    getUnsyncedData,
    cleanOldData,
    updateSyncStats
  }
})
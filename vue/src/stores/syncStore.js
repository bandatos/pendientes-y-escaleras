/**
 ** Store único para manejar el estado de sincronización de Pinia
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
//Servicios propios:
import { LocalStorageService } from '../services/localStorage.js'
import { getApiSync } from '../services/apiSync.js'
import { getNetworkDetection } from '../services/networkDetection.js'

export const useSyncStore = defineStore('sync', () => {
  // Estado reactivo                     ⬆️id único    
  const report = ref({
    line: "",
    station: "",
    typeElevation: "",
    isWorking: true,
    evidenceImage: null,
    notes: "",
    date: new Date(),
  });
  //Add the dummy data.
const lines = ref([
  { line: "Línea 1", color: "#e9468f", name: "Observatorio - Pantitlán" },
  { line: "Línea 2", color: "#00599f", name: "Cuatro Caminos - Tasqueña" },
  { line: "Línea 3", color: "#b69c13", name: "Indios Verdes - Universidad" },
  { line: "Línea 4", color: "#6cbab1", name: "Martín Carrera - Santa Anita" },
  { line: "Línea 5", color: "#fdd200", name: "Pantitlán - Politécnico" },
  { line: "Línea 6", color: "#da1715", name: "El Rosario - Martín Carrera" },
  {
    line: "Línea 7",
    color: "#e97009",
    name: "El Rosario - Barranca del Muerto",
  },
  {
    line: "Línea 8",
    color: "#008e3d",
    name: "Garibaldi/Lagunilla - Constitución de 1917",
  },
  { line: "Línea 9", color: "#5b352e", name: "Tacubaya - Pantitlán" },
  { line: "Línea A", color: "#9e1a81", name: "Pantitlán - La Paz" },
  { line: "Línea B", color: "#bbb9b8", name: "Buenavista - Ciudad Azteca" },
  { line: "Línea 12", color: "#c49955", name: "Mixcoac - Tláhuac" },
]);
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
  const networkDetection = getNetworkDetection()



  // Computed properties (getters)
  const syncProgress = computed(() => {
    if (syncStats.value.total === 0) return 100
    return Math.round((syncStats.value.synced / syncStats.value.total) * 100)
  })

  const hasPendingData = computed(() => syncStats.value.pending > 0)

  // Inicializar store
  function init() {
    // Listener para cambios de conectividad
    networkDetection.addListener((online) => {
      isOnline.value = online
      if (online) {
        console.log('🟢 Store: Conexión restaurada')
      } else {
        console.log('🔴 Store: Conexión perdida')
      }
    })

    // Actualizar stats iniciales
    updateSyncStats()

    console.log('🏪 SyncStore inicializado')
  }

  // Actualizar estadísticas de sync
  function updateSyncStats() {
    const stats = apiSync.getSyncStats()
    syncStats.value = stats
    isSyncing.value = stats.isSyncing
  }

  // Guardar datos del formulario
  async function saveFormData(formData) {
    try {
      console.log('💾 Store: Guardando datos del formulario')
      
      // Guardar en localStorage
      const savedData = LocalStorageService.saveFormData(formData)
      
      // Actualizar estadísticas
      updateSyncStats()
      
      // Intentar sync inmediato si hay conexión
      if (isOnline.value) {
        console.log('🔄 Store: Intentando sync inmediato')
        syncPendingData()
      } else {
        console.log('⏸️ Store: Sin conexión - datos guardados localmente')
      }
      
      return savedData
    } catch (error) {
      console.error('❌ Store: Error guardando datos:', error)
      throw error
    }
  }

  // Sincronizar datos pendientes
  async function syncPendingData() {
    if (isSyncing.value) {
      console.log('⏳ Store: Sync ya en progreso')
      return
    }

    try {
      isSyncing.value = true
      console.log('🔄 Store: Iniciando sincronización')
      
      const result = await apiSync.syncPendingData()
      
      // Actualizar estadísticas
      updateSyncStats()
      
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
      
      console.log(`✅ Store: Sync completo - ${result.synced} exitosos, ${result.failed} fallidos`)
      return result
      
    } catch (error) {
      console.error('❌ Store: Error durante sync:', error)
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
  function getAllSavedData() {
    return LocalStorageService.getAllFormData()
  }

  // Obtener datos no sincronizados
  function getUnsyncedData() {
    return LocalStorageService.getUnsyncedData()
  }

  // Forzar sincronización manual
  async function forceSync() {
    console.log('🔄 Store: Forzando sync manual')
    return await syncPendingData()
  }

  // Limpiar datos antiguos
  function cleanOldData() {
    LocalStorageService.cleanOldData()
    updateSyncStats()
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

    //dummy data
    lines,
    
    // Computed
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

export default useSyncStore
/**
 * Store para manejar el progreso del relevamiento de una estación
 */
import { defineStore } from 'pinia'
import { ref, computed, toRaw } from 'vue'
import { IndexedDBService } from '../services/indexDB.js'
import { useStationStore } from '../stores/stationStore'
import { useImageStore } from '../stores/imageStore'
import { useSnackbarStore } from '../stores/snackbarStore'
import { stairsService } from '../services'

export const useSurveyStore = defineStore('survey', () => {

  const stationStore = useStationStore()

  // Función helper: Convertir objeto reactivo a objeto plano (deep)
  function toPlainObject(obj) {
    return JSON.parse(JSON.stringify(toRaw(obj)))
  }

  // Estado reactivo
  const currentSurvey = ref(null) // Relevamiento en progreso
  const currentStairIndex = ref(0) // Índice de escalera actual (0-based)
  const currentStairs = ref([]) // Escaleras de la estación seleccionada
  const isSaving = ref(false)

  // Computed properties
  const isActive = computed(() => currentSurvey.value !== null)

  const total_stairs = computed(() =>
    currentSurvey.value?.total_stairs || 0
  )

  const completedStairs = computed(() =>
    currentSurvey.value?.stairs.filter(s => s.status === 'completed').length || 0
  )

  const pendingStairs = computed(() =>
    total_stairs.value - completedStairs.value
  )

  const currentStair = computed(() =>
    currentSurvey.value?.stairs[currentStairIndex.value] || null
  )

  const isLastStair = computed(() =>
    currentStairIndex.value === total_stairs.value - 1
  )

  const progress = computed(() =>
    total_stairs.value > 0 ? Math.round((completedStairs.value / total_stairs.value) * 100) : 0
  )

  // Estadísticas del relevamiento
  const stats = computed(() => {
    if (!currentSurvey.value) return { working: 0, notWorking: 0 }

    // const working = currentSurvey.value.stairs.filter(s =>
    //   s.status === 'completed' && s.is_working === true
    // ).length
    const working = currentStairs.value.filter(s =>
      s.status === 'completed' && s.is_working === true
    ).length

    const notWorking = currentStairs.value.filter(s =>
      s.status === 'completed' && s.is_working === false
    ).length

    return { working, notWorking }
  })

  // Iniciar nuevo relevamiento de estación
  function startSurvey(station) {
    // console.log("stationStore", stationStore);
    // console.log("rawStairs", stationStore.rawStairs);
    currentStairs.value = stationStore.rawStairs.filter(
      s => s.station === station.id)
    console.log("currentStairs", currentStairs.value);

    // id: 1853
    // number: 2
    // station: 1203
    // stop: 2144
    const stairTemplates = currentStairs.value.map(s => {
      return {
        id: s.id,
        stair: s.id,
        number: s.number,
        stair_full: s,
        code_identifiers: [],
        hasCodes: false,

        // Puntos de conexión
        route_start: '',
        path_start: '',
        path_end: '',
        route_end: '',

        // Estado de mantenimiento
        status_maintenance: null, // 'minor' | 'major' | 'critical' | 'other'
        other_status_maintenance: '',

        // Estado operativo
        is_working: null,
        is_aligned: null, // Si la escalera está alineada correctamente

        details: '',
        photo_ids: [],
        image_urls: [],
        status: 'pending', // 'pending' | 'completed'

        // Sincronización con backend
        backend_id: null,
        synced: false,
        synced_at: null
      }
    })
    currentStairs.value = stairTemplates

    currentSurvey.value = {
      // Datos de la estación
      station_id: station.station_id,
      station_name: station.name,
      line: station.line,
      line_color: station.line_color,
      total_stairs: station.total_stairs,

      // Array de escaleras
      stairs: stairTemplates,

      // Estadísticas
      completedStairs: 0,
      stairsWorking: 0,
      stairsNotWorking: 0,

      // Metadata
      surveyStartedAt: Date.now(),
      surveyCompletedAt: null,
      status: 'in_progress'
    }

    currentStairIndex.value = 0

    // console.log(`📋 Relevamiento iniciado para: ${station.name} (${station.total_stairs} escaleras)`)
  }

  // Actualizar datos de escalera actual
  function updateCurrentStair(stairData) {
    if (!currentSurvey.value || !currentStair.value) return

    // Actualizar la escalera en el array
    currentSurvey.value.stairs[currentStairIndex.value] = {
      ...currentStair.value,
      ...stairData,
      status: 'completed'
    }

    console.log(`✅ Escalera ${currentStairIndex.value + 1} actualizada`)
  }

  // Navegar a siguiente escalera
  function nextStair() {
    if (currentStairIndex.value < total_stairs.value - 1) {
      currentStairIndex.value++
      console.log(`➡️ Avanzando a escalera ${currentStairIndex.value + 1}`)
      return true
    }
    return false
  }

  // Navegar a escalera anterior
  function previousStair() {
    if (currentStairIndex.value > 0) {
      currentStairIndex.value--
      console.log(`⬅️ Retrocediendo a escalera ${currentStairIndex.value + 1}`)
      return true
    }
    return false
  }

  // Ir a escalera específica
  function goToStair(index) {
    if (index >= 0 && index < total_stairs.value) {
      currentStairIndex.value = index
      console.log(`🎯 Navegando a escalera ${index + 1}`)
      return true
    }
    return false
  }

  // Guardar imágenes de la escalera actual
  async function saveCurrentStairImages(stationRecordId, fileObjects) {
    if (!currentStair.value || fileObjects.length === 0) return []

    try {
      const imageIds = await IndexedDBService.saveStairImages(
        stationRecordId,
        currentStair.value.number,
        fileObjects
      )

      // Guardar IDs en el survey
      currentStair.value.photo_ids = imageIds

      return imageIds
    } catch (error) {
      console.error('❌ Error guardando imágenes:', error)
      throw error
    }
  }

  /**
   * ----------Sincronzar escalera por escalera.-------
   * @param {Object} stair - Objeto de escalera con todos sus datos
   * @param {Array<File>} images - Array de imágenes (opcional)
   * @returns {Promise<Object>} - { success: boolean, reportId: number, error?: string }
   */
  async function syncSingleStair(stair, images = []) {
    try {
      // Preparar datos del reporte para api/stair_report/
      const reportData = {
        stair: stair.stair, // ID de la escalera del catálogo
        status_maintenance: stair.status_maintenance || 'minor',
        other_status_maintenance: stair.other_status_maintenance || '',
        code_identifiers: stair.code_identifiers || [],
        route_start: stair.route_start || '',
        path_start: stair.path_start || '',
        path_end: stair.path_end || '',
        route_end: stair.route_end || '',
        is_aligned: stair.is_aligned !== null ? stair.is_aligned : true,
        is_working: stair.is_working,
        details: stair.details || ''
      }

      console.log(`📤 Guardando escalera ${stair.number} (ID catálogo: ${stair.stair})...`)

      // 1. Guardar datos de la escalera
      const savedReport = await stairsService.saveStair(toPlainObject(reportData))

      console.log(`✅ Escalera ${stair.number} guardada con ID: ${savedReport.id}`)

      // 2. Subir imágenes si existen
      if (images && images.length > 0) {
        console.log(`📤 Subiendo ${images.length} imágenes para escalera ${stair.number}...`)

        try {
          const imageResponse = await stairsService.uploadStairImages(stair.stair, images)
          console.log(`✅ Imágenes subidas para escalera ${stair.number}`)

          // Guardar referencias de imágenes
          stair.photo_ids = imageResponse.photo_ids || []
          stair.image_urls = imageResponse.image_urls || []
        } catch (imageError) {
          console.warn(`⚠️ Error subiendo imágenes de escalera ${stair.number}:`, imageError.message)
          // No lanzar error, las imágenes son opcionales
        }
      }

      // 3. Marcar como sincronizada
      stair.backend_id = savedReport.id
      stair.synced = true
      stair.synced_at = Date.now()

      return {
        success: true,
        reportId: savedReport.id
      }

    } catch (error) {
      console.error(`❌ Error sincronizando escalera ${stair.number}:`, error.message)
      stair.synced = false

      return {
        success: false,
        error: error.message
      }
    }
  }

  // Completar relevamiento y guardar (con sincronización al backend si hay conexión)
  async function completeSurvey() {
    if (!currentSurvey.value) {
      throw new Error('No hay relevamiento activo')
    }

    const imageStore = useImageStore()
    const snackbarStore = useSnackbarStore()
    const isOnline = navigator.onLine

    try {
      isSaving.value = true

      console.log(`🔄 Guardando relevamiento (${isOnline ? 'online' : 'offline'})...`)

      let syncedCount = 0
      let failedCount = 0

      // Intentar sincronizar cada escalera con el backend (si hay conexión)
      if (isOnline) {
        for (let i = 0; i < currentStairs.value.length; i++) {
          const stair = currentStairs.value[i]
          const photos = imageStore.getStairPhotos(i)

          // Sincronizar escalera opr escalera.
          const result = await syncSingleStair(stair, photos)

          if (result.success) {
            syncedCount++
          } else {
            failedCount++
          }
        }

        // Mostrar resultado de sincronización
        if (syncedCount > 0) {
          snackbarStore.showSuccess(`${syncedCount} escalera(s) sincronizada(s) con el servidor`)
        }
        if (failedCount > 0) {
          snackbarStore.showWarning(`${failedCount} escalera(s) quedaron pendientes de sincronización`)
        }
      } else {
        console.log('📴 Sin conexión - guardando solo en local')
        snackbarStore.showInfo('Guardado en local (se sincronizará cuando haya conexión)')
      }

      // Actualizar estadísticas finales
      currentSurvey.value.completedStairs = completedStairs.value
      currentSurvey.value.stairsWorking = stats.value.working
      currentSurvey.value.stairsNotWorking = stats.value.notWorking
      currentSurvey.value.surveyCompletedAt = Date.now()
      currentSurvey.value.status = 'completed'

      // Convertir a objeto plano (sin reactividad) antes de guardar
      const plainSurvey = toPlainObject(currentSurvey.value)

      // SIEMPRE guardar en IndexedDB (backup local)
      const savedRecord = await IndexedDBService.saveStationRecord(plainSurvey)

      console.log('✅ Relevamiento completado y guardado localmente:', savedRecord.id)

      return savedRecord

    } catch (error) {
      console.error('❌ Error completando relevamiento:', error)
      snackbarStore.showError(`Error al guardar: ${error.message}`)
      throw error
    } finally {
      isSaving.value = false
    }
  }

  // Cancelar relevamiento actual
  function cancelSurvey() {
    currentSurvey.value = null
    currentStairIndex.value = 0
    console.log('❌ Relevamiento cancelado')
  }

  // Limpiar después de guardar
  function clearSurvey() {
    currentSurvey.value = null
    currentStairIndex.value = 0
    console.log('🧹 Relevamiento limpiado')
  }

  // Validar si escalera actual está completa
  function validateCurrentStair() {
    if (!currentStair.value) return { valid: false, errors: ['No hay escalera actual'] }

    const errors = []
    const stair = currentStair.value

    // Validar códigos (solo si no marcó "sin códigos")
    if (!stair.hasCodes && stair.code_identifiers.length === 0) {
      errors.push('Debe tener al menos un código de identificación')
    }

    // Validar puntos de conexión
    if (!stair.route_start) {
      errors.push('Debe especificar el origen del recorrido')
    }

    if (!stair.path_end) {
      errors.push('Debe especificar dónde termina la escalera')
    }

    // Validar estado operativo
    if (stair.is_working === null) {
      errors.push('Debe indicar si la escalera funciona')
    }

    // Validar estado de mantenimiento
    if (!stair.status_maintenance) {
      errors.push('Debe indicar el estado de mantenimiento')
    }

    // Validar queel campo other sea completado
    if (stair.status_maintenance === 'other' && !stair.other_status_maintenance) {
      errors.push('Debe especificar el estado de mantenimiento personalizado')
    }

    // Validar alineación
    if (stair.is_aligned === null) {
      errors.push('Debe indicar si la escalera está alineada')
    }

    // Si no funciona, requiere foto
    if (stair.is_working === false && stair.photo_ids.length === 0) {
      errors.push('Si no funciona, debe adjuntar al menos 1 foto')
    }

    return {
      valid: errors.length === 0,
      errors
    }
  }

  /**
   * Re-sincronizar escaleras pendientes
   * Busca en IndexedDB todas las escaleras con synced: false y las envía al servidor
   */
  async function syncPendingStairs() {
    const imageStore = useImageStore()
    const snackbarStore = useSnackbarStore()

    if (!navigator.onLine) {
      console.log('📴 Sin conexión - no se puede sincronizar')
      snackbarStore.showWarning('Sin conexión a internet')
      return { synced: 0, failed: 0, total: 0 }
    }

    try {
      console.log('🔄 Buscando escaleras pendientes de sincronización...')

      // Obtener todos los registros de estaciones desde IndexedDB
      const allRecords = await IndexedDBService.getAllStationRecords()

      if (!allRecords || allRecords.length === 0) {
        console.log('✅ No hay registros guardados')
        return { synced: 0, failed: 0, total: 0 }
      }

      // Buscar escaleras no sincronizadas en todos los registros
      const pendingStairs = []
      allRecords.forEach(record => {
        if (record.stairs && Array.isArray(record.stairs)) {
          record.stairs.forEach((stair, index) => {
            if (!stair.synced) {
              pendingStairs.push({
                stair,
                stairIndex: index,
                recordId: record.id,
                station_id: record.station_id
              })
            }
          })
        }
      })

      if (pendingStairs.length === 0) {
        console.log('✅ No hay escaleras pendientes de sincronización')
        return { synced: 0, failed: 0, total: 0 }
      }

      console.log(`📊 Encontradas ${pendingStairs.length} escaleras pendientes`)

      let syncedCount = 0
      let failedCount = 0

      // Sincronizar cada escalera usando la función modular
      for (const { stair, stairIndex, recordId } of pendingStairs) {
        // Usar la función modular para sincronizar
        const result = await syncSingleStair(stair)

        if (result.success) {
          // Actualizar el registro en IndexedDB
          const record = allRecords.find(r => r.id === recordId)
          if (record) {
            await IndexedDBService.updateStationRecord(recordId, { stairs: record.stairs })
          }
          syncedCount++
        } else {
          failedCount++
        }
      }

      const result = {
        synced: syncedCount,
        failed: failedCount,
        total: pendingStairs.length
      }

      // Mostrar resultado al usuario
      if (syncedCount > 0) {
        snackbarStore.showSuccess(`${syncedCount} escalera(s) sincronizada(s)`)
      }
      if (failedCount > 0) {
        snackbarStore.showWarning(`${failedCount} escalera(s) no se pudieron sincronizar`)
      }

      console.log(`✅ Re-sincronización completa:`, result)
      return result

    } catch (error) {
      console.error('❌ Error durante re-sincronización:', error)
      snackbarStore.showError(`Error en sincronización: ${error.message}`)
      throw error
    }
  }

  /**
   * Obtener estadísticas de sincronización
   * Cuenta cuántas escaleras están pendientes de sincronizar
   */
  async function getSyncStats() {
    try {
      const allRecords = await IndexedDBService.getAllStationRecords()

      let totalStairs = 0
      let syncedStairs = 0
      let pendingStairs = 0

      allRecords.forEach(record => {
        if (record.stairs && Array.isArray(record.stairs)) {
          record.stairs.forEach(stair => {
            totalStairs++
            if (stair.synced) {
              syncedStairs++
            } else {
              pendingStairs++
            }
          })
        }
      })

      return {
        total: totalStairs,
        synced: syncedStairs,
        pending: pendingStairs
      }
    } catch (error) {
      console.error('Error obteniendo stats de sincronización:', error)
      return { total: 0, synced: 0, pending: 0 }
    }
  }

  return {
    // Estado
    currentSurvey,
    currentStairIndex,
    isSaving,
    currentStairs,

    // Computed
    isActive,
    total_stairs,
    completedStairs,
    pendingStairs,
    currentStair,
    isLastStair,
    progress,
    stats,

    // Acciones
    startSurvey,
    updateCurrentStair,
    nextStair,
    previousStair,
    goToStair,
    saveCurrentStairImages,
    completeSurvey,
    cancelSurvey,
    clearSurvey,
    validateCurrentStair,
    syncPendingStairs,
    getSyncStats
  }
})

export default useSurveyStore

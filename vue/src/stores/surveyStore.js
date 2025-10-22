/**
 * Store para manejar el progreso del relevamiento de una estación
 */
import { defineStore } from 'pinia'
import { ref, computed, toRaw } from 'vue'
import { IndexedDBService } from '../services/indexDB.js'
import { useStationStore } from '../stores/stationStore'

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

    const working = currentSurvey.value.stairs.filter(s =>
      s.status === 'completed' && s.is_working === true
    ).length

    const notWorking = currentSurvey.value.stairs.filter(s =>
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
        stair: s.id,
        number: s.number,
        stair_full: s,
        code_identifiers: [],
        hasCodes: false,
        route_start: '',
        path_start: '',
        path_end: '',
        route_end: '',
        details: '',
        is_working: null,
        photo_ids: [],
        status: 'pending' // 'pending' | 'completed'
      }
    })

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

    console.log(`📋 Relevamiento iniciado para: ${station.name} (${station.total_stairs} escaleras)`)
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

  // Completar relevamiento y guardar en IndexedDB
  async function completeSurvey() {
    if (!currentSurvey.value) {
      throw new Error('No hay relevamiento activo')
    }

    try {
      isSaving.value = true

      // Actualizar estadísticas finales
      currentSurvey.value.completedStairs = completedStairs.value
      currentSurvey.value.stairsWorking = stats.value.working
      currentSurvey.value.stairsNotWorking = stats.value.notWorking
      currentSurvey.value.surveyCompletedAt = Date.now()
      currentSurvey.value.status = 'completed'

      // Convertir a objeto plano (sin reactividad) antes de guardar
      const plainSurvey = toPlainObject(currentSurvey.value)

      // Guardar en IndexedDB
      const savedRecord = await IndexedDBService.saveStationRecord(plainSurvey)

      console.log('✅ Relevamiento completado y guardado:', savedRecord.id)

      return savedRecord

    } catch (error) {
      console.error('❌ Error completando relevamiento:', error)
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

    // Validaciones
    if (currentStair.value.code_identifiers.length === 0) {
      errors.push('Debe tener al menos un código de identificación')
    }

    if (!currentStair.value.route_start) {
      errors.push('Debe especificar el punto inicial')
    }

    if (currentStair.value.is_working === null) {
      errors.push('Debe indicar si la escalera funciona')
    }

    if (currentStair.value.is_working === false && currentStair.value.photo_ids.length === 0) {
      errors.push('Si no funciona, debe adjuntar al menos 1 foto')
    }

    return {
      valid: errors.length === 0,
      errors
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
    validateCurrentStair
  }
})

export default useSurveyStore

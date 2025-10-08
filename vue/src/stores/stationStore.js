/**
 * Store para manejar el catálogo de estaciones y selección actual
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { IndexedDBService } from '../services/indexDB.js'

export const useStationStore = defineStore('station', () => {

  // Estado reactivo
  const stationsCatalog = ref([]) // Catálogo completo de estaciones
  const selectedStation = ref(null) // Estación actualmente seleccionada
  const isLoading = ref(false)

  // Computed properties
  const hasStations = computed(() => stationsCatalog.value.length > 0)

  const stationsByLine = computed(() => {
    const grouped = {}
    stationsCatalog.value.forEach(station => {
      if (!grouped[station.line]) {
        grouped[station.line] = []
      }
      grouped[station.line].push(station)
    })
    return grouped
  })

  // Inicializar catálogo de estaciones
  async function init() {
    try {
      isLoading.value = true

      // Cargar desde IndexedDB
      const catalog = await IndexedDBService.getStationsCatalog()

      if (catalog.length === 0) {
        // Si no hay datos, poblar con datos iniciales
        console.log('📋 Catálogo vacío, poblando con datos iniciales...')
        await seedInitialStations()
      } else {
        stationsCatalog.value = catalog
        console.log(`✅ Catálogo cargado: ${catalog.length} estaciones`)
      }

    } catch (error) {
      console.error('❌ Error inicializando catálogo:', error)
    } finally {
      isLoading.value = false
    }
  }

  // Poblar catálogo inicial (datos del metro de CDMX)
  async function seedInitialStations() {
    const initialStations = [
      // Línea 1
      { stationId: 'observatorio', name: 'Observatorio', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 2 },
      { stationId: 'tacubaya_l1', name: 'Tacubaya', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 4 },
      { stationId: 'juanacatlan', name: 'Juanacatlán', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 2 },
      { stationId: 'chapultepec', name: 'Chapultepec', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 3 },
      { stationId: 'sevilla', name: 'Sevilla', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 2 },
      { stationId: 'insurgentes', name: 'Insurgentes', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 4 },
      { stationId: 'cuauhtemoc', name: 'Cuauhtémoc', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 2 },
      { stationId: 'balderas_l1', name: 'Balderas', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 3 },
      { stationId: 'salto_agua', name: 'Salto del Agua', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 3 },
      { stationId: 'isabel_catolica', name: 'Isabel la Católica', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 2 },
      { stationId: 'pino_suarez_l1', name: 'Pino Suárez', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 4 },
      { stationId: 'merced', name: 'Merced', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 2 },
      { stationId: 'candelaria', name: 'Candelaria', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 3 },
      { stationId: 'san_lazaro', name: 'San Lázaro', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 4 },
      { stationId: 'moctezuma', name: 'Moctezuma', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 2 },
      { stationId: 'balbuena', name: 'Balbuena', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 2 },
      { stationId: 'pantitlan_l1', name: 'Pantitlán', line: 'Línea 1', lineColor: '#e9468f', totalStairs: 5 },

      // Línea 8 (ejemplo)
      { stationId: 'garibaldi', name: 'Garibaldi/Lagunilla', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 3 },
      { stationId: 'bellas_artes', name: 'Bellas Artes', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 4 },
      { stationId: 'san_juan_letran', name: 'San Juan de Letrán', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'salto_agua_l8', name: 'Salto del Agua', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 3 },
      { stationId: 'doctores', name: 'Doctores', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'obrera', name: 'Obrera', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'chabacano_l8', name: 'Chabacano', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 3 },
      { stationId: 'la_viga', name: 'La Viga', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'santa_anita_l8', name: 'Santa Anita', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 3 },
      { stationId: 'coyuya', name: 'Coyuya', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'iztacalco', name: 'Iztacalco', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'apatlaco', name: 'Apatlaco', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'aculco', name: 'Aculco', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'escuadron_201', name: 'Escuadrón 201', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'atlalilco', name: 'Atlalilco', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 3 },
      { stationId: 'iztapalapa', name: 'Iztapalapa', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'cerro_estrella', name: 'Cerro de la Estrella', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'uam_i', name: 'UAM-I', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 2 },
      { stationId: 'constitucion_1917', name: 'Constitución de 1917', line: 'Línea 8', lineColor: '#008e3d', totalStairs: 4 },
    ]

    await IndexedDBService.seedStations(initialStations)
    stationsCatalog.value = initialStations
    console.log('✅ Catálogo inicial poblado')
  }

  // Seleccionar una estación
  function selectStation(station) {
    selectedStation.value = station
    console.log('📍 Estación seleccionada:', station.name)
  }

  // Limpiar selección
  function clearSelection() {
    selectedStation.value = null
  }

  // Buscar estación por ID
  async function getStationById(stationId) {
    const station = await IndexedDBService.getStationById(stationId)
    return station
  }

  // Buscar estaciones por línea
  function getStationsByLine(line) {
    return stationsCatalog.value.filter(s => s.line === line)
  }

  return {
    // Estado
    stationsCatalog,
    selectedStation,
    isLoading,

    // Computed
    hasStations,
    stationsByLine,

    // Acciones
    init,
    selectStation,
    clearSelection,
    getStationById,
    getStationsByLine,
    seedInitialStations
  }
})

export default useStationStore

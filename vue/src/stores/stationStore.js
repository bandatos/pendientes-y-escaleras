/**
 * Store para manejar el catálogo de estaciones y selección actual
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { IndexedDBService } from '../services/indexDB.js'
import { catalogsService } from '../services'
const SERVICE = catalogsService

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

  // Request the data to the endpoint.
  async function init() {
    try {
      isLoading.value = true

      // Cargar desde IndexedDB
      const catalog = await IndexedDBService.getStationsCatalog()

      if (catalog.length === 0) {
        // Si no hay datos, poblar con datos iniciales
        console.log('📋 Catálogo vacío, requiriendo catálogo')

        await SERVICE.getCatalogs()
          .then(response => {
            //Store in the state.
            console.debug(response);  
          }, error => {
            console.error('Error al obtener los catálogos', error);
          })
          .finally(() => {
            console.log('Finish :>> ');
          })

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
      { station_id: 'observatorio', name: 'Observatorio', line: 'Línea 1', line_color: '#e9468f', total_stairs: 2 },
      { station_id: 'tacubaya_l1', name: 'Tacubaya', line: 'Línea 1', line_color: '#e9468f', total_stairs: 4 },
      { station_id: 'juanacatlan', name: 'Juanacatlán', line: 'Línea 1', line_color: '#e9468f', total_stairs: 2 },
      { station_id: 'chapultepec', name: 'Chapultepec', line: 'Línea 1', line_color: '#e9468f', total_stairs: 3 },
      { station_id: 'sevilla', name: 'Sevilla', line: 'Línea 1', line_color: '#e9468f', total_stairs: 2 },
      { station_id: 'insurgentes', name: 'Insurgentes', line: 'Línea 1', line_color: '#e9468f', total_stairs: 4 },
      { station_id: 'cuauhtemoc', name: 'Cuauhtémoc', line: 'Línea 1', line_color: '#e9468f', total_stairs: 2 },
      { station_id: 'balderas_l1', name: 'Balderas', line: 'Línea 1', line_color: '#e9468f', total_stairs: 3 },
      { station_id: 'salto_agua', name: 'Salto del Agua', line: 'Línea 1', line_color: '#e9468f', total_stairs: 3 },
      { station_id: 'isabel_catolica', name: 'Isabel la Católica', line: 'Línea 1', line_color: '#e9468f', total_stairs: 2 },
      { station_id: 'pino_suarez_l1', name: 'Pino Suárez', line: 'Línea 1', line_color: '#e9468f', total_stairs: 4 },
      { station_id: 'merced', name: 'Merced', line: 'Línea 1', line_color: '#e9468f', total_stairs: 2 },
      { station_id: 'candelaria', name: 'Candelaria', line: 'Línea 1', line_color: '#e9468f', total_stairs: 3 },
      { station_id: 'san_lazaro', name: 'San Lázaro', line: 'Línea 1', line_color: '#e9468f', total_stairs: 4 },
      { station_id: 'moctezuma', name: 'Moctezuma', line: 'Línea 1', line_color: '#e9468f', total_stairs: 2 },
      { station_id: 'balbuena', name: 'Balbuena', line: 'Línea 1', line_color: '#e9468f', total_stairs: 2 },
      { station_id: 'pantitlan_l1', name: 'Pantitlán', line: 'Línea 1', line_color: '#e9468f', total_stairs: 5 },

      // Línea 8 (ejemplo)
      { station_id: 'garibaldi', name: 'Garibaldi/Lagunilla', line: 'Línea 8', line_color: '#008e3d', total_stairs: 3 },
      { station_id: 'bellas_artes', name: 'Bellas Artes', line: 'Línea 8', line_color: '#008e3d', total_stairs: 4 },
      { station_id: 'san_juan_letran', name: 'San Juan de Letrán', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'salto_agua_l8', name: 'Salto del Agua', line: 'Línea 8', line_color: '#008e3d', total_stairs: 3 },
      { station_id: 'doctores', name: 'Doctores', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'obrera', name: 'Obrera', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'chabacano_l8', name: 'Chabacano', line: 'Línea 8', line_color: '#008e3d', total_stairs: 3 },
      { station_id: 'la_viga', name: 'La Viga', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'santa_anita_l8', name: 'Santa Anita', line: 'Línea 8', line_color: '#008e3d', total_stairs: 3 },
      { station_id: 'coyuya', name: 'Coyuya', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'iztacalco', name: 'Iztacalco', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'apatlaco', name: 'Apatlaco', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'aculco', name: 'Aculco', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'escuadron_201', name: 'Escuadrón 201', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'atlalilco', name: 'Atlalilco', line: 'Línea 8', line_color: '#008e3d', total_stairs: 3 },
      { station_id: 'iztapalapa', name: 'Iztapalapa', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'cerro_estrella', name: 'Cerro de la Estrella', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'uam_i', name: 'UAM-I', line: 'Línea 8', line_color: '#008e3d', total_stairs: 2 },
      { station_id: 'constitucion_1917', name: 'Constitución de 1917', line: 'Línea 8', line_color: '#008e3d', total_stairs: 4 },
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
  async function getStationById(station_id) {
    const station = await IndexedDBService.getStationById(station_id)
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

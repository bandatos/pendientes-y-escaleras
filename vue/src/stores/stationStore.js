/**
 * Store para manejar el catálogo de estaciones y selección actual
 */
import { IndexedDBService } from '@/services/indexDB.js'
import { catalogsService } from '@/services'
import { useSnackbarStore } from '@/stores/'

const SERVICE = catalogsService

export const useStationStore = defineStore('station', () => {

  // Estado reactivo
  const selectedStation = ref(null) // Estación actualmente seleccionada
  const isLoading = ref(false)

  // Datos raw del API (estructura relacional)
  const rawRoutes = ref([]) // Líneas del metro
  const rawStops = ref([]) // Stops (paradas por línea)
  const rawStations = ref([]) // Estaciones físicas
  const rawStairs = ref([]) // Escaleras
  const fullStations = ref([])

  // Computed properties
  // Empty computed properties for future use

  /**
   * Transforma los datos relacionales del API al formato normalizado para la UI
   * Entrada: { routes: [], stops: [], stations: [], stairs: [] }
   * Salida: [{ station_id, name, line, line_color, total_stairs, ... }, ...]
   */

  function buildFullStations(apiData) {
  console.debug(apiData);
    const routesById = apiData.routes.reduce((acc, route) => {
      acc[route.id] = route
      return acc
    }, {})

    // Contar escaleras por estación
    const stairsByStation = {}
    apiData.stairs.forEach(stair => {
      const stationId = stair.station
      let total = (stairsByStation[stationId]?.total || 0) + 1
      let is_working = (stairsByStation[stationId]?.is_working || 0)
      let is_not_working = (stairsByStation[stationId]?.is_not_working || 0)
      let with_report = (stairsByStation[stationId]?.with_report || 0)

      stairsByStation[stationId] = {
        total: total,
        is_working: is_working + (stair.is_working === true ? 1 : 0),
        is_not_working: is_not_working + (stair.is_working === false ? 1 : 0),
        with_report: typeof(stair.is_working) === 'boolean' ? with_report + 1 : with_report,
      }
    })
    //
    // const stairsCountByStation = {}
    // apiData.stairs.forEach(stair => {
    //   const station_id = stair.station
    //   stairsCountByStation[station_id] =
    //     (stairsCountByStation[station_id] || 0) + 1
    // })

    return apiData.stations.map(station => {
      const routes_full = station.routes.map(routeId =>
          routesById[routeId] || null)
      const first_route = routes_full[0] || {}
      let station_full = {
        ...station,
        ...station.viz_params,
        // routes_full,
        line_color: `#${first_route.route_color || '000000'}`,
        first_route: first_route,
        total_stairs: stairsByStation[station.id]?.total || 0,
        stairs_working: stairsByStation[station.id]?.is_working || 0,
        stairs_not_working: stairsByStation[station.id]?.is_not_working || 0,
        stairs_with_report: stairsByStation[station.id]?.with_report || 0,
      }
      if (station.routes.length > 1) {
        // console.log(`Estación con múltiples líneas: ${station.name} (${station.routes.length})`)
        // console.log("routes_full:", routes_full);
        station_full.line_colors = routes_full.map(
          r => `#${r.route_color}`)
        const lines = routes_full.map(r => r.route_short_name)
        station_full.lines = lines.join(', ')
        station_full.lines_text = `Líneas ${station_full.lines}`
      }
      return station_full
    })
  }

  // Request the data to the endpoint.
  async function init() {
    const snackbarStore = useSnackbarStore()

    try {
      isLoading.value = true

      // Cargar desde IndexedDB primero (para mostrar algo mientras carga del API)
      const cachedCatalog = await IndexedDBService.getStationsCatalog()

      if (navigator.onLine) {
        // Con conexión: Siempre intentar actualizar desde el API
        console.log('🌐 Conexión disponible, actualizando catálogo desde API...')

        try {
          const apiData = await SERVICE.getCatalogs()

          if (!apiData || !apiData.stations) {
            throw new Error('Datos del API inválidos')
          }

          
          // Fill data from api
          const full_stations = updateStationStore(apiData)
          fullStations.value = full_stations

          // Guardar en IndexedDB para uso offline
          await IndexedDBService.updateStationsCatalog(full_stations)
          // Guardar para valores obtenidos por raw, por si se va la conexión.
          await IndexedDBService.addRawDataBackup(apiData);
          // await IndexedDBService.seedStations(full_stations)

          /* console.log(`✅ Catálogo actualizado desde API: ${full_stations.length} estaciones`)
          console.log(`   - ${rawRoutes.value.length} líneas`)
          console.log(`   - ${rawStops.value.length} stops`)
          console.log(`   - ${rawStations.value.length} estaciones físicas`)
          console.log(`   - ${rawStairs.value.length} escaleras`) */

        } catch (error) {
          // Si falla el API pero hay cache, usar el cache
          console.warn('⚠️ Error del API, usando cache:', error.message)

          if (cachedCatalog.length > 0) {
          //Fill data from Storage
            const indexDBData = await IndexedDBService.getRawData();
            const full_stations = updateStationStore(indexDBData[0])
            fullStations.value = full_stations

            console.log(`✅ Usando catálogo en cache: ${full_stations.length} estaciones`)
            snackbarStore.showWarning('Usando catálogo local (sin actualizar)')
          } else {
            // Sin Storage y sin API = error fatal
            throw new Error('No hay conexión al servidor y no hay datos en cache')
          }
        }

      } else {
        // Sin conexión: Usar cache
        console.log('📴 Sin conexión, usando catálogo en cache...')

        if (cachedCatalog.length > 0) {
          //Fill data from Storage
          const indexDBData = await IndexedDBService.getRawData() //indexDBStorage
          const full_stations = updateStationStore(indexDBData[0])
          fullStations.value = full_stations;
          console.log(`✅ Catálogo cargado desde cache: ${cachedCatalog.length} estaciones`)
          snackbarStore.showInfo('Modo offline: usando catálogo local')
        } else {
          throw new Error('No hay datos en cache y no hay conexión')
        }
      }

    } catch (error) {
      console.error('❌ Error inicializando catálogo:', error)
      snackbarStore.showError(`Error cargando catálogo: ${error.message}`)
    } finally {
      isLoading.value = false
    }
  }

  function updateStationStore(data) { //update
      // Guardar datos raw en el store
      rawRoutes.value = data.routes || []
      rawStops.value = data.stops || []
      rawStations.value = data.stations || []
      rawStairs.value = data.stairs || []
    
    const full_stations = buildFullStations(data)
    return full_stations;
  }

  // Seleccionar una estación
  function selectStation(station) {
    selectedStation.value = station
    console.log('📍 Estación seleccionada:', station.name)
  }

  // Limpiar selección
  function clearSelection() {
    selectedStation.value = null
    // currentStairs.value = []
  }

  // Buscar estación por ID
  async function getStationById(station_id) {
    const station = await IndexedDBService.getStationById(station_id)
    return station
  }

  return {
    // Estado
    selectedStation,
    isLoading,

    // Datos raw del API
    rawRoutes,
    rawStops,
    rawStations,
    rawStairs,
    fullStations,
    // Computed

    // Acciones
    init,
    selectStation,
    clearSelection,
    getStationById,
  }
})


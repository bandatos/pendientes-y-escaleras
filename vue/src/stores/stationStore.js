/**
 * Store para manejar el catálogo de estaciones y selección actual
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { IndexedDBService } from '../services/indexDB.js'
import { catalogsService } from '../services'
import { useSnackbarStore } from './snackbarStore.js'

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
  function transformCatalogData(apiData) {

    const routesById = apiData.routes.reduce((acc, route) => {
      acc[route.id] = route
      return acc
    }, {})

    // Contar escaleras por estación
    const stairsByStation = {}
    apiData.stairs.forEach(stair => {
      const stationId = stair.station
      stairsByStation[stationId] = (stairsByStation[stationId] || 0) + 1
    })

    // Agrupar stops por estación para saber qué rutas pasan por cada estación
    const stopsByStation = {}
    apiData.stops.forEach(stop => {
      const stationId = stop.station
      if (!stopsByStation[stationId]) {
        stopsByStation[stationId] = []
      }
      stopsByStation[stationId].push(stop)
    })

    // Transformar cada estación física (versión simple para stationsCatalog)
    return apiData.stations.map(station => {
      // Obtener la línea principal de esta estación
      const mainRoute = routesById[station.main_route]

      if (!mainRoute) {
        console.warn(`Estación ${station.name} no tiene main_route válida`)
        return null
      }

      return {
        // Usar el ID del backend directamente (normalizado)
        station_id: station.id,
        name: station.name,
        line: `Línea ${mainRoute.route_short_name}`,
        line_color: `#${mainRoute.route_color}`,
        total_stairs: stairsByStation[station.id] || 0,

        // Datos adicionales útiles
        main_route: mainRoute.id,
        viz_params: station.viz_params // Para el mapa D3.js Futura consideración
      }
    }).filter(Boolean) // Eliminar nulls
  }

  function buildFullStations(apiData) {
    const routesById = apiData.routes.reduce((acc, route) => {
      acc[route.id] = route
      return acc
    }, {})

    const stairsCountByStation = {}
    apiData.stairs.forEach(stair => {
      const station_id = stair.station
      stairsCountByStation[station_id] =
        (stairsCountByStation[station_id] || 0) + 1
    })

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
        total_stairs: stairsCountByStation[station.id] || 0,
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

          // Guardar datos raw en el store
          rawRoutes.value = apiData.routes || []
          rawStops.value = apiData.stops || []
          rawStations.value = apiData.stations || []
          rawStairs.value = apiData.stairs || []

          // Transformar datos al formato de la UI

          const full_stations = buildFullStations(apiData)
          fullStations.value = full_stations

          // Guardar en IndexedDB para uso offline
          await IndexedDBService.updateStationsCatalog(full_stations)
          // await IndexedDBService.seedStations(full_stations)

          console.log(`✅ Catálogo actualizado desde API: ${full_stations.length} estaciones`)
          console.log(`   - ${rawRoutes.value.length} líneas`)
          console.log(`   - ${rawStops.value.length} stops`)
          console.log(`   - ${rawStations.value.length} estaciones físicas`)
          console.log(`   - ${rawStairs.value.length} escaleras`)

        } catch (error) {
          // Si falla el API pero hay cache, usar el cache
          console.warn('⚠️ Error del API, usando cache:', error.message)

          if (cachedCatalog.length > 0) {
            fullStations.value = cachedCatalog
            console.log(`✅ Usando catálogo en cache: ${cachedCatalog.length} estaciones`)
            snackbarStore.showWarning('Usando catálogo local (sin actualizar)')
          } else {
            // Sin cache y sin API = error fatal
            throw new Error('No hay conexión al servidor y no hay datos en cache')
          }
        }

      } else {
        // Sin conexión: Usar cache
        console.log('📴 Sin conexión, usando catálogo en cache...')

        if (cachedCatalog.length > 0) {
          fullStations.value = cachedCatalog
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


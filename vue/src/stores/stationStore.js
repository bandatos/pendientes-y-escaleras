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
  const stationsCatalog = ref([]) // Catálogo transformado para la UI
  const selectedStation = ref(null) // Estación actualmente seleccionada
  const isLoading = ref(false)

  // Datos raw del API (estructura relacional)
  const rawRoutes = ref([]) // Líneas del metro
  const rawStops = ref([]) // Stops (paradas por línea)
  const rawStations = ref([]) // Estaciones físicas
  const rawStairs = ref([]) // Escaleras
  const dictRoutesById = ref({}) // Lookup de líneas por ID
  const fullStations = ref([])

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

  /**
   * Transforma los datos relacionales del API al formato normalizado para la UI
   * Entrada: { routes: [], stops: [], stations: [], stairs: [] }
   * Salida: [{ station_id, name, line, line_color, total_stairs, ... }, ...]
   */
  function transformCatalogData(apiData) {
    // Crear lookups para acceso rápido
    const routesById = {}
    apiData.routes.forEach(route => {
      routesById[route.id] = route
    })

    // Contar escaleras por estación
    const stairsByStation = {}
    apiData.stairs.forEach(stair => {
      const stationId = stair.station
      stairsByStation[stationId] = (stairsByStation[stationId] || 0) + 1
    })

    // Transformar cada estación física
    const transformed = apiData.stations.map(station => {
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

    return transformed
  }

  // Request the data to the endpoint.
  async function init() {
    const snackbarStore = useSnackbarStore()

    try {
      isLoading.value = true

      // Cargar desde IndexedDB
      const catalog = await IndexedDBService.getStationsCatalog()

      // if (catalog.length === 0) {
        // Si no hay datos en cache, obtener del API
        console.log('📋 Catálogo vacío, fetching desde API...')

        const apiData = await SERVICE.getCatalogs()
        console.debug(apiData);
        if (!apiData || !apiData.stations) {
          throw new Error('Datos del API inválidos')
        }

        // Guardar datos raw en el store
        rawRoutes.value = apiData.routes || []
        rawStops.value = apiData.stops || []
        rawStations.value = apiData.stations || []
        rawStairs.value = apiData.stairs || []
        dictRoutesById.value = {}
        rawRoutes.value.forEach(route => {
          dictRoutesById.value[route.id] = route
        })

        fullStations.value = rawStations.value.map(station => {
          const routes_full = station.routes.map(routeId =>
              dictRoutesById.value[routeId] || null)
          const first_route = routes_full[0] || {}
          let station_full = {
            ...station,
            // routes_full,
            line_color: `#${first_route.route_color || '000000'}`,
            first_route: first_route,
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

        // Transformar datos al formato de la UI
        const transformedCatalog = transformCatalogData(apiData)
        stationsCatalog.value = transformedCatalog

        // Guardar en IndexedDB para uso offline
        await IndexedDBService.seedStations(transformedCatalog)

        console.log(`✅ Catálogo descargado y transformado: ${transformedCatalog.length} estaciones`)
        console.log(`   - ${rawRoutes.value.length} líneas`)
        console.log(`   - ${rawStops.value.length} stops`)
        console.log(`   - ${rawStations.value.length} estaciones físicas`)
        console.log(`   - ${rawStairs.value.length} escaleras`)

      // } else {
        // Cargar desde cache
        // stationsCatalog.value = catalog
        console.log(`✅ Catálogo cargado desde cache: ${catalog.length} estaciones`)
      // }

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

  // Buscar estaciones por línea
  function getStationsByLine(line) {
    return stationsCatalog.value.filter(s => s.line === line)
  }

  return {
    // Estado
    stationsCatalog,
    selectedStation,
    isLoading,

    // Datos raw del API
    rawRoutes,
    rawStops,
    rawStations,
    rawStairs,
    dictRoutesById,
    fullStations,

    // Computed
    hasStations,
    stationsByLine,

    // Acciones
    init,
    transformCatalogData,
    selectStation,
    clearSelection,
    getStationById,
    getStationsByLine
  }
})

export default useStationStore

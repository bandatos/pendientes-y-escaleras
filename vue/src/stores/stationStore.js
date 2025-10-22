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
  const stationsCatalog = ref([]) // Catálogo transformado
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

    // Guardar en dictRoutesById para acceso global
    dictRoutesById.value = routesById

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

    // Transformar para fullStations (versión completa con todas las rutas)
    const fullTransformed = apiData.stations.map(station => {
      const mainRoute = routesById[station.main_route]

      if (!mainRoute) {
        return null
      }

      // Obtener todas las rutas que pasan por esta estación
      const stopsOfStation = stopsByStation[station.id] || []
      const routesOfStation = stopsOfStation
        .map(stop => routesById[stop.route])
        .filter(Boolean)
        .filter((route, index, self) =>
          // Eliminar duplicados por ID
          index === self.findIndex(r => r.id === route.id)
        )

      // Crear arrays de colores y números de línea
      const lineColors = routesOfStation.map(r => `#${r.route_color}`)
      const lineNumbers = routesOfStation.map(r => r.route_short_name)
      const linesText = routesOfStation.map(r => `Línea ${r.route_short_name}`).join(', ')

      return {
        id: station.id,
        name: station.name,
        total_stairs: stairsByStation[station.id] || 0,

        // Primera ruta (principal)
        first_route: {
          id: mainRoute.id,
          route_short_name: mainRoute.route_short_name,
          route_desc: mainRoute.route_desc,
          line_color: `#${mainRoute.route_color}`
        },

        // Todas las rutas
        routes: routesOfStation,
        line_colors: lineColors,
        lines: lineNumbers.join('-'),
        lines_text: linesText,

        // Datos adicionales
        viz_params: station.viz_params
      }
    }).filter(Boolean)

    // Guardar fullStations
    fullStations.value = fullTransformed

    return transformed
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
          const transformedCatalog = transformCatalogData(apiData)
          stationsCatalog.value = transformedCatalog

          // Guardar en IndexedDB para uso offline
          await IndexedDBService.seedStations(transformedCatalog)

          console.log(`✅ Catálogo actualizado desde API: ${transformedCatalog.length} estaciones`)
          console.log(`   - ${rawRoutes.value.length} líneas`)
          console.log(`   - ${rawStops.value.length} stops`)
          console.log(`   - ${rawStations.value.length} estaciones físicas`)
          console.log(`   - ${rawStairs.value.length} escaleras`)

        } catch (error) {
          // Si falla el API pero hay cache, usar el cache
          console.warn('⚠️ Error del API, usando cache:', error.message)

          if (cachedCatalog.length > 0) {
            stationsCatalog.value = cachedCatalog
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
          stationsCatalog.value = cachedCatalog
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

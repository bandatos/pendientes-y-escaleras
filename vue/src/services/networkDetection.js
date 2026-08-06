/**
 * Network Detection Service para monitorear conectividad
 */

export class NetworkDetectionService {
  constructor() {
    this.isOnline = navigator.onLine
    this.listeners = new Set()
    this.setupEventListeners()
  }

  // Configurar listeners de eventos de red
  setupEventListeners() {
    window.addEventListener('online', () => {
      console.log('🟢 Conexión restaurada')
      this.isOnline = true
      this.notifyListeners(true)
    })

    window.addEventListener('offline', () => {
      console.log('🔴 Conexión perdida')
      this.isOnline = false
      this.notifyListeners(false)
    })
  }

  // Obtener estado actual de conectividad
  getConnectionStatus() {
    return this.isOnline
  }

/* Añadir listner a los eventos y eliminarlos. */
  addListener(listener) {
    this.listeners.add(listener);
  }

  removeListener(listener) {
    this.listeners.delete(listener);
  }



  // Notificar a todos los listeners del cambio de estado
  notifyListeners(isOnline) {
    this.listeners.forEach(callback => {
      try {
        callback(isOnline)
      } catch (error) {
        console.error('Error notifying network listener:', error)
      }
    })
  }

  // Test de conectividad real (ping al servidor)
  async testRealConnectivity(url = 'https://httpbin.org/status/200', timeout = 5000) {
    if (!this.isOnline) {
      return false
    }

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)

      const response = await fetch(url, {
        method: 'HEAD',
        mode: 'no-cors',
        signal: controller.signal,
        cache: 'no-cache'
      })

      clearTimeout(timeoutId)
      return true
    } catch (error) {
      console.warn('Real connectivity test failed:', error.message)
      return false
    }
  }

  // Destructor para limpiar event listeners
  destroy() {
    window.removeEventListener('online', this.handleOnline)
    window.removeEventListener('offline', this.handleOffline)
    this.listeners.clear()
  }
}

// Singleton instance
let networkDetectionInstance = null

export function getNetworkDetection() {
  if (!networkDetectionInstance) {
    networkDetectionInstance = new NetworkDetectionService()
  }
  return networkDetectionInstance
}

export default NetworkDetectionService
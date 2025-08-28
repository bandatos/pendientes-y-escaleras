/**
 * API Sync Service - Coordina la sincronización con el servidor
 */
import { LocalStorageService } from './localStorage.js'
import { getNetworkDetection } from './networkDetection.js'

export class ApiSyncService {
  constructor(apiBaseUrl = 'https://jsonplaceholder.typicode.com') {
    this.apiBaseUrl = apiBaseUrl
    this.networkDetection = getNetworkDetection()
    this.isSyncing = false
    this.retryAttempts = 3
    this.retryDelay = 1000 // 1 segundo inicial
    
    // Listener para auto-sync cuando se restaure la conexión
    this.networkDetection.addListener((isOnline) => {
      if (isOnline && !this.isSyncing) {
        console.log('🔄 Conexión restaurada - Iniciando auto-sync')
        setTimeout(() => this.syncPendingData(), 2000) // Delay de 2s para estabilidad
      }
    })
  }

  // Sincronizar datos pendientes
  async syncPendingData() {
    if (this.isSyncing) {
      console.log('⏳ Sync ya en progreso...')
      return
    }

    this.isSyncing = true
    console.log('🔄 Iniciando sincronización...')

    try {
      const pendingData = LocalStorageService.getSyncQueue()
      console.log(`📊 ${pendingData.length} elementos pendientes por sincronizar`)

      if (pendingData.length === 0) {
        console.log('✅ No hay datos pendientes')
        return { success: true, synced: 0, failed: 0 }
      }

      const results = await this.syncBatch(pendingData)
      
      console.log(`✅ Sync completo: ${results.synced} exitosos, ${results.failed} fallidos`)
      return results

    } catch (error) {
      console.error('❌ Error durante sync:', error)
      return { success: false, error: error.message }
    } finally {
      this.isSyncing = false
    }
  }


  async syncBatch(pendingData) {
    let synced = 0;
    let failed = 0;
    for await (const element of pendingData) {
      try {
        //Send post one by one.
        const save = await this.syncSingleItem(element);
        if (save.success) {
          synced += 1;
        } else {
          failed += 1;
        }
      } catch (error) {
        console.error('No se pudo sincronizar el item');
        failed += 1;
      }
    }
    return { synced, failed }
  }

  // Sincronizar un elemento individual con reintentos
  async syncSingleItem(item, attempt = 1) {
    try {
      console.log(`🔄 Sincronizando item ${item.id} (intento ${attempt}/${this.retryAttempts})`)

      // Verificar conectividad real antes del envío
      const isConnected = await this.networkDetection.testRealConnectivity()
      if (!isConnected) {
        throw new Error('No hay conectividad real')
      }

      // Enviar al API (simulamos con JSONPlaceholder)
      const response = await fetch(`${this.apiBaseUrl}/posts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: `Survey: Line ${item.line}, Station ${item.station}`,
          body: JSON.stringify(item),
          userId: 1
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      console.log(`✅ Item ${item.id} sincronizado exitosamente`)

      // Marcar como sincronizado en localStorage
      LocalStorageService.markAsSynced(item.id)
      
      return { success: true, data: result }

    } catch (error) {
      console.error(`❌ Error sincronizando item ${item.id}:`, error.message)

      // Reintentar si no hemos agotado los intentos
      if (attempt < this.retryAttempts) {
        const delay = this.retryDelay * Math.pow(2, attempt - 1) // Exponential backoff
        console.log(`⏳ Reintentando en ${delay}ms...`)
        
        await this.sleep(delay)
        return this.syncSingleItem(item, attempt + 1)
      }

      return { success: false, error: error.message }
    }
  }

  // Función auxiliar para delays
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  // Obtener estadísticas de sync
  getSyncStats() {
    const allData = LocalStorageService.getAllFormData()
    const unsynced = LocalStorageService.getUnsyncedData()
    
    return {
      total: allData.length,
      synced: allData.length - unsynced.length,
      pending: unsynced.length,
      isSyncing: this.isSyncing
    }
  }

  // Forzar sync manual
  async forcSync() {
    console.log('🔄 Forzando sincronización manual...')
    return await this.syncPendingData()
  }
}

// Singleton instance
let apiSyncInstance = null

export function getApiSync(apiBaseUrl) {
  if (!apiSyncInstance) {
    apiSyncInstance = new ApiSyncService(apiBaseUrl)
  }
  return apiSyncInstance
}

export default ApiSyncService
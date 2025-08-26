/**
 * Local Storage Service para manejo de datos offline
 */

const STORAGE_KEYS = {
  SYNC_QUEUE: 'surveyApp_syncQueue',
  FORM_DATA: 'surveyApp_formData',
  LAST_SYNC: 'surveyApp_lastSync'
}

export class LocalStorageService {
  
  // Guardar datos del formulario
  /* Método estático para solo usarse con el constructor */
  static saveFormData(formData) {
    try {
      const dataWithId = {
        ...formData,
        id: this.generateId(),
        timestamp: Date.now(),
        synced: false
      }
      
      const existingData = this.getAllFormData()
      existingData.push(dataWithId)
      
      localStorage.setItem(STORAGE_KEYS.FORM_DATA, JSON.stringify(existingData))
      
      // Agregar a la cola de sincronización
      this.addToSyncQueue(dataWithId)
      
      return dataWithId
    } catch (error) {
      console.error('Error saving form data:', error)
      throw error
    }
  }

  // Obtener todos los datos del formulario
  static getAllFormData() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.FORM_DATA)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Error retrieving form data:', error)
      return []
    }
  }


  //Agregar a la queue
  static addToSyncQueue(data) {
    try {
      const queue = this.getSyncQueue();
      queue.push(data);

      localStorage.setItem(STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(queue));

    } catch (error) {
      console.error('Error to try to add to Queue');
    }
  }

  //getSyncQueue
  static getSyncQueue() {
    //Siempre tenemos strings
    const queueString = localStorage.getItem(STORAGE_KEYS.SYNC_QUEUE);
    return queueString ? JSON.parse(queueString) : []; //Convertimso string -> array
  }

  static removeFromSyncQueue(id) {
    try {
      let queue = this.getSyncQueue();
      queue = queue.filter(data => data.id != id);

      //Actualizar una vez que removimos
      localStorage.setItem(STORAGE_KEYS.SYNC_QUEUE, JSON.stringify(queue));

    } catch (error) {
      console.error('Error to remove', error);
    }
  }

  // Marcar datos como sincronizados
  static markAsSynced(id) {
    try {
      const allData = this.getAllFormData()
      const updatedData = allData.map(item => 
        item.id === id ? { ...item, synced: true, syncedAt: Date.now() } : item
      )
      
      localStorage.setItem(STORAGE_KEYS.FORM_DATA, JSON.stringify(updatedData))
      this.removeFromSyncQueue(id)
    } catch (error) {
      console.error('Error marking as synced:', error)
    }
  }

  // Generar ID único
  static generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }

  // Obtener datos no sincronizados
  static getUnsyncedData() {
    return this.getAllFormData().filter(item => !item.synced)
  }

  // Limpiar datos antiguos (más de 30 días)
  static cleanOldData() {
    try {
      const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000)
      const allData = this.getAllFormData()
      const recentData = allData.filter(item => 
        item.timestamp > thirtyDaysAgo || !item.synced
      )
      
      localStorage.setItem(STORAGE_KEYS.FORM_DATA, JSON.stringify(recentData))
    } catch (error) {
      console.error('Error cleaning old data:', error)
    }
  }
}

export default LocalStorageService
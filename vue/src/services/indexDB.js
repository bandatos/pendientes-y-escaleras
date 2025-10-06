/**
 * IndexedDB Service usando Dexie
 * Reemplaza localStorage para mejor manejo de imágenes y datos offline
 */
import Dexie from 'dexie';

// Crear base de datos
const db = new Dexie('relevamientoMetro');

// Schema versión 1 - Replica estructura de localStorage
db.version(1).stores({
    // Datos de formularios (equivalente a FORM_DATA)
    formData: 'id, timestamp, synced, line, station',

    // Cola de sincronización (equivalente a PENDING_SYNC_QUEUE)
    syncQueue: 'id, timestamp, synced',

    // Imágenes guardadas como File objects (NUEVO - antes eran base64)
    images: '++id, formId, timestamp, synced',

    // Catálogo de estaciones (opcional, para tu prueba)
    stations: '++id, stair_id, station, line'
});

// Hooks de inicialización
db.on('ready', () => {
    console.log('🗄️ IndexedDB inicializada:', db.name);
});

// Exportar instancia
export { db };

// Clase de servicio que replica LocalStorageService
export class IndexedDBService {

    // Guardar datos del formulario
    static async saveFormData(formData) {
        try {
            const dataWithId = {
                ...formData,
                id: this.generateId(),
                timestamp: Date.now(),
                synced: false
            };

            // Guardar en tabla formData
            await db.formData.add(dataWithId);

            // Agregar a la cola de sincronización
            await this.addToSyncQueue(dataWithId);

            console.log('✅ Formulario guardado en IndexedDB:', dataWithId.id);
            return dataWithId;

        } catch (error) {
            console.error('❌ Error saving form data:', error);
            throw error;
        }
    }

    // Obtener todos los datos del formulario
    static async getAllFormData() {
        try {
            const data = await db.formData.toArray();
            return data;
        } catch (error) {
            console.error('❌ Error retrieving form data:', error);
            return [];
        }
    }

    // Agregar a la queue
    static async addToSyncQueue(data) {
        try {
            await db.syncQueue.add(data);
            console.log('📋 Agregado a cola de sincronización');
        } catch (error) {
            console.error('❌ Error adding to sync queue:', error);
        }
    }

    // Obtener cola de sincronización
    static async getSyncQueue() {
        try {
            const queue = await db.syncQueue.toArray();
            return queue;
        } catch (error) {
            console.error('❌ Error getting sync queue:', error);
            return [];
        }
    }

    // Remover de la cola de sincronización
    static async removeFromSyncQueue(id) {
        try {
            await db.syncQueue.delete(id);
            console.log('✅ Removido de cola:', id);
        } catch (error) {
            console.error('❌ Error removing from queue:', error);
        }
    }

    // Marcar datos como sincronizados
    static async markAsSynced(id) {
        try {
            // Actualizar en formData
            await db.formData.update(id, {
                synced: true,
                syncedAt: Date.now()
            });

            // Remover de syncQueue
            await this.removeFromSyncQueue(id);

            console.log('✅ Marcado como sincronizado:', id);
        } catch (error) {
            console.error('❌ Error marking as synced:', error);
        }
    }

    // Generar ID único (mismo método que localStorage)
    static generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    // Obtener datos no sincronizados
    static async getUnsyncedData() {
        try {
            const unsynced = await db.formData
                .where('synced')
                .equals(false)
                .toArray();
            return unsynced;
        } catch (error) {
            console.error('❌ Error getting unsynced data:', error);
            return [];
        }
    }

    // Limpiar datos antiguos (más de 30 días)
    static async cleanOldData(daysToKeep = 30) {
        try {
            const cutoffDate = Date.now() - (daysToKeep * 24 * 60 * 60 * 1000);

            // Solo eliminar datos sincronizados y antiguos
            await db.formData
                .where('synced').equals(true)
                .and(item => item.timestamp < cutoffDate)
                .delete();

            console.log('🧹 Datos antiguos limpiados');
        } catch (error) {
            console.error('❌ Error cleaning old data:', error);
        }
    }

    // NUEVO: Guardar imágenes como File objects
    static async saveImages(formId, fileObjects) {
        try {
            const imageRecords = fileObjects.map((file, index) => ({
                formId: formId,
                file: file, // File object directo, NO base64
                order: index,
                timestamp: Date.now(),
                synced: false,
                s3Key: null
            }));

            // Guardar todas las imágenes
            const ids = await db.images.bulkAdd(imageRecords, { allKeys: true });

            console.log(`✅ ${fileObjects.length} imágenes guardadas para form ${formId}`);
            return ids;

        } catch (error) {
            console.error('❌ Error saving images:', error);
            throw error;
        }
    }

    // NUEVO: Obtener imágenes de un formulario
    static async getImagesByFormId(formId) {
        try {
            const images = await db.images
                .where('formId')
                .equals(formId)
                .sortBy('order'); // Mantener orden original
            return images;
        } catch (error) {
            console.error('❌ Error getting images:', error);
            return [];
        }
    }

    // NUEVO: Marcar imagen como sincronizada
    static async markImageAsSynced(imageId, s3Key, s3Url) {
        try {
            await db.images.update(imageId, {
                synced: true,
                syncedAt: Date.now(),
                s3Key: s3Key,
                s3Url: s3Url
            });
            console.log('✅ Imagen sincronizada:', imageId);
        } catch (error) {
            console.error('❌ Error marking image as synced:', error);
        }
    }
}

export default IndexedDBService;
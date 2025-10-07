/**
 * IndexedDB Service usando Dexie
 * Reemplaza localStorage para mejor manejo de imágenes y datos offline
 */
import Dexie from 'dexie';

// Crear base de datos
const db = new Dexie('relevamientoMetro');

// Schema versión 1 - DEPRECADO (modelo antiguo)
db.version(1).stores({
    formData: 'id, timestamp, synced, line, station',
    syncQueue: 'id, timestamp, synced',
    images: '++id, formId, timestamp, synced',
    stations: '++id, stair_id, station, line'
});

// Schema versión 2 - Nuevo modelo: 1 registro por estación con N escaleras
db.version(2).stores({
    // Registros completos de estaciones con todas sus escaleras
    stationRecords: 'id, stationId, timestamp, synced, status, line',

    // Imágenes vinculadas a estación + escalera específica
    images: '++id, stationRecordId, stairNumber, synced, timestamp, s3Key',

    // Catálogo de estaciones (metadata estática del sistema)
    stations: '++id, stationId, name, line, totalStairs',

    // Cola de sincronización
    syncQueue: '++id, type, entityId, priority, timestamp'
}).upgrade(async tx => {
    // Migración de datos de v1 a v2 (si hay datos antiguos)
    console.log('🔄 Migrando datos de versión 1 a versión 2...');

    // Los datos antiguos quedan en formData (deprecated)
    // Nuevos datos usan stationRecords
    // Puedes migrar manualmente si es necesario
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

    // ==========================================
    // NUEVO MODELO V2: Station Records
    // ==========================================

    // Guardar registro completo de estación con todas sus escaleras
    static async saveStationRecord(stationData) {
        try {
            const record = {
                ...stationData,
                id: this.generateId(),
                timestamp: Date.now(),
                synced: false,
                status: stationData.status || 'completed'
            };

            await db.stationRecords.add(record);
            console.log('✅ Estación guardada en IndexedDB:', record.id);

            // Agregar a cola de sincronización
            await this.addToSyncQueue({
                id: this.generateId(),
                type: 'station',
                entityId: record.id,
                priority: 1,
                timestamp: Date.now()
            });

            return record;
        } catch (error) {
            console.error('❌ Error saving station record:', error);
            throw error;
        }
    }

    // Obtener todos los registros de estaciones
    static async getAllStationRecords() {
        try {
            const records = await db.stationRecords.toArray();
            return records;
        } catch (error) {
            console.error('❌ Error getting station records:', error);
            return [];
        }
    }

    // Obtener registros de estaciones no sincronizados
    static async getUnsyncedStationRecords() {
        try {
            const unsynced = await db.stationRecords
                .where('synced')
                .equals(false)
                .toArray();
            return unsynced;
        } catch (error) {
            console.error('❌ Error getting unsynced stations:', error);
            return [];
        }
    }

    // Marcar estación como sincronizada
    static async markStationAsSynced(stationRecordId) {
        try {
            await db.stationRecords.update(stationRecordId, {
                synced: true,
                syncedAt: Date.now()
            });

            // Remover de cola
            await db.syncQueue
                .where('entityId')
                .equals(stationRecordId)
                .delete();

            console.log('✅ Estación sincronizada:', stationRecordId);
        } catch (error) {
            console.error('❌ Error marking station as synced:', error);
        }
    }

    // Guardar imágenes para una escalera específica de una estación
    static async saveStairImages(stationRecordId, stairNumber, fileObjects) {
        try {
            const imageRecords = fileObjects.map((file, index) => ({
                stationRecordId: stationRecordId,
                stairNumber: stairNumber,
                file: file,
                order: index,
                timestamp: Date.now(),
                synced: false,
                s3Key: null,
                s3Url: null
            }));

            const ids = await db.images.bulkAdd(imageRecords, { allKeys: true });

            console.log(`✅ ${fileObjects.length} imágenes guardadas para estación ${stationRecordId}, escalera ${stairNumber}`);
            return ids;

        } catch (error) {
            console.error('❌ Error saving stair images:', error);
            throw error;
        }
    }

    // Obtener imágenes de una escalera específica
    static async getStairImages(stationRecordId, stairNumber) {
        try {
            const images = await db.images
                .where('[stationRecordId+stairNumber]')
                .equals([stationRecordId, stairNumber])
                .sortBy('order');
            return images;
        } catch (error) {
            console.error('❌ Error getting stair images:', error);
            return [];
        }
    }

    // Obtener todas las imágenes de una estación
    static async getAllStationImages(stationRecordId) {
        try {
            const images = await db.images
                .where('stationRecordId')
                .equals(stationRecordId)
                .toArray();
            return images;
        } catch (error) {
            console.error('❌ Error getting station images:', error);
            return [];
        }
    }

    // Marcar imagen de escalera como sincronizada
    static async markStairImageAsSynced(imageId, s3Key, s3Url) {
        try {
            await db.images.update(imageId, {
                synced: true,
                syncedAt: Date.now(),
                s3Key: s3Key,
                s3Url: s3Url
            });
            console.log('✅ Imagen de escalera sincronizada:', imageId);
        } catch (error) {
            console.error('❌ Error marking stair image as synced:', error);
        }
    }

    // Seed: Poblar catálogo de estaciones (solo desarrollo/testing)
    static async seedStations(stationsData) {
        try {
            await db.stations.bulkAdd(stationsData);
            console.log(`✅ ${stationsData.length} estaciones agregadas al catálogo`);
        } catch (error) {
            console.error('❌ Error seeding stations:', error);
        }
    }

    // Obtener catálogo de estaciones
    static async getStationsCatalog() {
        try {
            const stations = await db.stations.toArray();
            return stations;
        } catch (error) {
            console.error('❌ Error getting stations catalog:', error);
            return [];
        }
    }

    // Buscar estación en catálogo por ID
    static async getStationById(stationId) {
        try {
            const station = await db.stations
                .where('stationId')
                .equals(stationId)
                .first();
            return station;
        } catch (error) {
            console.error('❌ Error getting station:', error);
            return null;
        }
    }
}

export default IndexedDBService;
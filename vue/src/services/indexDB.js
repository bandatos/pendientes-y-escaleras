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

// Schema versión 2 - DEPRECADO (tenía conflicto de índices)
db.version(2).stores({
    formData: null, // Eliminar tabla antigua
    stationRecords: 'id, station_id, timestamp, synced, status, line',
    images: null, // Eliminar para recrear
    stations: '++id, station_id, name, line, total_stairs',
    syncQueue: '++id, type, entityId, priority, timestamp'
});

// Schema versión 3 - Modelo final corregido
db.version(3).stores({
    // Registros completos de estaciones con todas sus escaleras
    stationRecords: 'id, station_id, timestamp, synced, status, line',
    // Raw data for getCatalogs
    rawData: '++id, routes, stops, stations, stairs',

    // Imágenes vinculadas a estación + escalera específica
    images: '++id, stationRecordId, number, synced, timestamp, s3Key',
    evidence_images: '++id, stair_id, synced, timestamp, s3Key, s3Url, finished, stair_report_id',
    // Catálogo de estaciones (metadata estática del sistema)
    stations: '++id, station_id, name, first_route, total_stairs',

    // Cola de sincronización
    syncQueue: '++id, type, entityId, priority, timestamp'
}).upgrade(async tx => {
    console.log('🔄 Actualizando a versión 3 - esquema limpio');
    // Las tablas se recrean automáticamente con el nuevo esquema
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

    // Actualizar un registro de estación
    static async updateStationRecord(stationRecordId, updates) {
        try {
            await db.stationRecords.update(stationRecordId, updates);
            console.log(`✅ Registro de estación ${stationRecordId} actualizado`);
        } catch (error) {
            console.error('❌ Error updating station record:', error);
            throw error;
        }
    }

    // Rick: Esto yo lo agregué manualmente para probar
    static async saveStairImage(stair_id, file) {
        try {
            const newId = await db.evidence_images.add({
                stair_id,
                file,
                timestamp: Date.now(),
                synced: false,
                s3Key: null,
                s3Url: null,
                finished: false
            });
            console.log(`✅ Imagen guardada para escalera ${stair_id}`);
            return newId;
        } catch (error) {
            console.error('❌ Error saving stair image:', error);
            throw error;
        }
    }

    // Guardar imágenes para una escalera específica de una estación
    static async saveStairImages(stationRecordId, number, fileObjects) {
        try {
            const imageRecords = fileObjects.map((file, index) => ({
                stationRecordId: stationRecordId,
                number: number,
                file: file,
                order: index,
                timestamp: Date.now(),
                synced: false,
                s3Key: null,
                s3Url: null
            }));

            const ids = await db.images.bulkAdd(imageRecords, { allKeys: true });

            console.log(`✅ ${fileObjects.length} imágenes guardadas para estación ${stationRecordId}, escalera ${number}`);
            return ids;

        } catch (error) {
            console.error('❌ Error saving stair images:', error);
            throw error;
        }
    }

    // Obtener imágenes de una escalera específica
    static async getStairImages(stationRecordId, number) {
        try {
            const images = await db.images
                .where('[stationRecordId+number]')
                .equals([stationRecordId, number])
                .sortBy('order');
            return images;
        } catch (error) {
            console.error('❌ Error getting stair images:', error);
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

    // Eliminar imágenes de una escalera específica (después de sincronizar)
    static async deleteStairImages(stationRecordId, number) {
        try {
            const deleted = await db.images
                .where('[stationRecordId+number]')
                .equals([stationRecordId, number])
                .delete();
            console.log(`🗑️ ${deleted} imágenes eliminadas para estación ${stationRecordId}, escalera ${number}`);
            return deleted;
        } catch (error) {
            console.error('❌ Error deleting stair images:', error);
            throw error;
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
    // Seed: Actualizar catálogo de estaciones (reemplazar todo)
    static async updateStationsCatalog(stationsData) {
        try {
            // Borrar catálogo existente
            await db.stations.clear();
            console.log('🗑️ Catálogo de estaciones limpiado');

            // Agregar nuevo catálogo
            await db.stations.bulkAdd(stationsData);
            console.log(`✅ Catálogo actualizado con ${stationsData.length} estaciones`);
        } catch (error) {
            console.error('❌ Error updating stations catalog:', error);
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
    static async getStationById(station_id) {
        try {
            const station = await db.stations
                .where('station_id')
                .equals(station_id)
                .first();
            return station;
        } catch (error) {
            console.error('❌ Error getting station:', error);
            return null;
        }
    }

    // DESARROLLO: Eliminar completamente la base de datos
    static async deleteDatabase() {
        try {
            await db.delete();
            console.log('🗑️ Base de datos eliminada completamente');
            console.log('🔄 Recarga la página para recrear la base de datos');
        } catch (error) {
            console.error('❌ Error deleting database:', error);
        }
    }

    // DESARROLLO: Resetear y recrear la base de datos
    static async resetDatabase() {
        try {
            await this.deleteDatabase();
            // La recarga automática recreará la DB con el esquema v3
            window.location.reload();
        } catch (error) {
            console.error('❌ Error resetting database:', error);
        }
    }

    static async addRawDataBackup(apiData) {
        try {
            //Add all the data as one register
            await db.rawData.add(apiData);

        } catch (error) {
            console.debug('Error adding the rawData', error);
        }
    }

    static async getRawData() {
        try {
            const rawData = await db.rawData.toArray();
            return rawData;
        } catch (error) {
            console.error('❌ Error getting stations catalog:', error);
            return [];
        }
    }
}

export default IndexedDBService;
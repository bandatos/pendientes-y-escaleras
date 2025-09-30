import Dexie from 'dexie';

const db = new Dexie('dbLocal');

db.version(1).stores({
    stations: 'station, line',
    /* images: 'File , stair_id', */
});

console.log('🗄️ IndexedDB inicializada:', db.name);

async function startingDB() {
    try {
        console.log('📥 Agregando estación de prueba...');
        
        // Verificar si ya existe la estación
        const existing = await db.stations.where('station').equals('Chapultepec').first();
        
        if (!existing) {
            await db.stations.add({ station: 'Chapultepec', line: 'Línea 1' });
            console.log('✅ Estación agregada correctamente');
        } else {
            console.log('ℹ️ La estación ya existe en la base de datos');
        }
    
        const info = await db.stations.toArray();
        console.log('📋 Estaciones en IndexedDB:', info);
        console.log('🔢 Total de estaciones:', info.length);

    } catch (error) {
        console.error('❌ Error en IndexedDB:', error);
    }
}

// Inicializar la base de datos
startingDB();
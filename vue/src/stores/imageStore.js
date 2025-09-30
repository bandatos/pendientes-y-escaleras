import { defineStore } from "pinia";
import { ref, computed } from "vue"

import { parseDocToB64 } from "../helpers/helpers.js"

export const useImageStore = defineStore('imageStore', () => {

//State
    /* const evidencesImages = ref([]); */
    const isUpdating = ref(false);
    const tag = ref('Componente para subir foto o tomar foto.');
    const modelPhoto = ref([]);

   


    //Actions
    // Convertir un solo archivo a base64
    async function convertBase64(document) {
        const file = await parseDocToB64(document);
        return file;
    }

    // Convertir múltiples archivos a base64
    async function convertMultipleBase64(files) {
        try {
            isUpdating.value = true;

            // Validar que no haya más de 3 archivos
            if (files.length > 3) {
                throw new Error('Máximo 3 imágenes permitidas');
            }

            // Convertir todos los archivos en paralelo
            const conversions = files.map(file => parseDocToB64(file));
            const results = await Promise.all(conversions);

            console.log(`✅ Convertidas ${results.length} imágenes a base64`);
            return results;
        } catch (error) {
            console.error('❌ Error convirtiendo múltiples imágenes:', error);
            throw error;
        } finally {
            isUpdating.value = false;
        }
    }


    return {
        //State
        tag,
        modelPhoto,
        isUpdating,

        //Actions
        convertBase64,
        convertMultipleBase64,
    }
});

export default useImageStore;
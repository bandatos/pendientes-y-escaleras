import { defineStore } from "pinia";
import { ref, computed } from "vue"
import { IndexedDBService } from "../services/indexDB.js"

export const useImageStore = defineStore('imageStore', () => {

//State
    const isUpdating = ref(false);
    const tag = ref('Componente para subir foto o tomar foto.');
    const modelPhoto = ref({}); // Objeto: { stairId: [File, File, ...] }


    //Actions
    // Validar imágenes (hasta 3)
    function validateImages(files) {
        if (!files || files.length === 0) {
            return { valid: false, message: 'No se seleccionaron imágenes' };
        }

        if (files.length > 3) {
            return { valid: false, message: 'Máximo 3 imágenes permitidas' };
        }

        // Validar que sean imágenes
        const invalidFiles = files.filter(file => !file.type.startsWith('image/'));
        if (invalidFiles.length > 0) {
            return { valid: false, message: 'Algunos archivos no son imágenes' };
        }

        // Validar tamaño (por ejemplo, 5MB por imagen)
        const maxSize = 5 * 1024 * 1024; // 5MB
        const oversized = files.filter(file => file.size > maxSize);
        if (oversized.length > 0) {
            return { valid: false, message: 'Algunas imágenes superan 5MB' };
        }

        return { valid: true };
    }

    // Guardar imágenes directamente en IndexedDB (sin conversión base64)
    async function saveImages(formId, files) {
        try {
            isUpdating.value = true;

            // Validar
            const validation = validateImages(files);
            if (!validation.valid) {
                throw new Error(validation.message);
            }

            // Guardar File objects directamente en IndexedDB
            const imageIds = await IndexedDBService.saveImages(formId, files);

            console.log(`✅ ${files.length} imágenes guardadas en IndexedDB (File objects)`);
            return imageIds;

        } catch (error) {
            console.error('❌ Error guardando imágenes:', error);
            throw error;
        } finally {
            isUpdating.value = false;
        }
    }

    // Obtener imágenes de un formulario
    async function getImages(formId) {
        try {
            const images = await IndexedDBService.getImagesByFormId(formId);
            return images;
        } catch (error) {
            console.error('❌ Error obteniendo imágenes:', error);
            return [];
        }
    }

    // Limpiar selección de imágenes de una escalera específica
    function clearSelection(stairId) {
      if (stairId !== undefined) {
        delete modelPhoto.value[stairId];
      } else {
        // Limpiar todas
        modelPhoto.value = {};
      }
    }

    // Obtener imágenes de una escalera específica
    function getStairPhotos(stairId) {
      return modelPhoto.value[stairId] || [];
    }

    // Establecer imágenes para una escalera específica
    function setStairPhotos(stairId, files) {
      const existingPhotos = modelPhoto.value[stairId] || [];
      modelPhoto.value[stairId] = existingPhotos.concat(files);
    }


    return {
        //State
        tag,
        modelPhoto,
        isUpdating,

        //Actions
        validateImages,
        saveImages,
        getImages,
        clearSelection,
        getStairPhotos,
        setStairPhotos,
    }
});
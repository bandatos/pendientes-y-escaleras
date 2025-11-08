import { defineStore } from "pinia";
import { ref, computed } from "vue"
import { IndexedDBService } from "../services/indexDB.js"

export const useImageStore = defineStore('imageStore', () => {

  //State
  const isUpdating = ref(false);
  const tag = ref('Componente para subir foto o tomar foto.');
  const modelPhoto = ref({}); // Objeto: { stairId: [File, File, ...] }

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
    clearSelection,
    getStairPhotos,
    setStairPhotos,
  }
});
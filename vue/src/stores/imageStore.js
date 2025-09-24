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
    async function convertBase64(document) {
        const file = await parseDocToB64(document);
        return file;
    }


    return {
        //State
        tag,
        modelPhoto,

        //Actions
        convertBase64,
    }
});

export default useImageStore;
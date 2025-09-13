import { defineStore } from "pinia";
import { ref, computed } from "vue"

export const imageStore = defineStore('imageStore', () => {

//State
    const evidencesImages = ref([]);
    const isUpdating = ref(false);

    //Initialize store
    function init() {
        
    }

});

export default imageStore;
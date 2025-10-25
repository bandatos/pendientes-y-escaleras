<script setup>
import { computed } from "vue";
import { useImageStore } from "../stores/imageStore";

const store = useImageStore();

const props = defineProps({
  title: {
    type: String,
    default: "Subir Evidencia.",
  },
  typeFiles: {
    type: String,
  },
  stairId: {
    type: [String, Number],
    required: true,
  },
});

// Computed para manejar v-model con el estado específico de esta escalera
const localPhotos = computed({
  get() {
    return store.getStairPhotos(props.stairId);
  },
  set(files) {
    store.setStairPhotos(props.stairId, files);
  }
});

const rules = [
  (files) => !files || files.length <= 3 || "-- Máximo 3 imágenes por escalera.",
];
</script>
<template>
  <v-row>
    <v-col>
      <v-file-input
        v-model="localPhotos"
        :label="title"
        accept="image/png, image/jpeg, image/jpg"
        multiple
        counter
        show-size
        chips
      >
        <template v-slot:selection="{ fileNames }">
          <template v-for="(fileName, index) in fileNames" :key="fileName">
            <v-chip
              v-if="index < 3"
              color="primary"
              size="small"
              label
              class="me-2"
            >
              {{ fileName }}
            </v-chip>
          </template>
        </template>
      </v-file-input>
    </v-col>
  </v-row>
</template>
<style scoped>
</style>
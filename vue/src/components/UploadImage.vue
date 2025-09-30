<script setup>
import { ref } from "vue";
import { useImageStore } from "../stores/imageStore";
import { storeToRefs } from "pinia";

const store = useImageStore();
/* Destructuring from a store */
const { tag, modelPhoto } = storeToRefs(store);

const props = defineProps({
  title: {
    type: String,
    default: "Subir Evidencia.",
  },
  typeFiles: {
    type: String,
  },
});

const rules = [
  (files) => !files || files.length <= 3 || "Máximo 3 imágenes por escalera.",
];
</script>
<template>
  <span>{{ tag }}</span>
  <v-row>
    <v-col>
      <v-file-input
        v-model="modelPhoto"
        :label="title"
        accept="image/png, image/jpeg, image/jpg"
        multiple
        counter
        show-size
        chips
        :rules="rules"
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
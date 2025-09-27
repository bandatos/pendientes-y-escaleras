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
</script>
<template>
  <span>{{ tag }}</span>
  <v-row>
    <v-col>
      <v-file-input
        v-model="modelPhoto"
        :label="title"
        accept="image/png, image/jpeg, image/jpg"
      ></v-file-input>
    </v-col>
  </v-row>
</template>
<style scoped>
</style>
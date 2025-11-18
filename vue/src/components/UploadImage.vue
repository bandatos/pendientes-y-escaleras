<script setup>
import { useImageStore } from "@/stores/imageStore";

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

const all_photos = ref([]);
const ascertainable = ref([]);

// Computed para manejar v-model con el estado específico de esta escalera
const localPhotos = computed({
  get() {
    // console.log("localPhotos", store.getStairPhotos(props.stairId))
    return store.getStairPhotos(props.stairId);
  },
  set(files) {
    store.setStairPhotos(props.stairId, files);
  },
});

function addFiles(e) {
  let files = e.target.files || e.dataTransfer.files;
  // console.log("files", files)
  for (let file of files) {
    const short_name = file.name;
    let final_elem = {
      ...{ stair: props.stairId },
      ...{ file: file },
      ...short_name,
    };
    ascertainable.value.push(final_elem);
  }
  // this.saveFiles()
}
</script>

<template>
  <v-row>
    <input
      type="file"
      :id="stairId"
      class="d-none"
      multiple
      @change="addFiles($event)"
    />

    <v-col cols="12">
      <v-btn
        color="primary"
        variant="outlined"
        prepend-icon="photo"
        @click="$refs.fileInput.click()"
      >
        Agregar foto(s)
      </v-btn>
    </v-col>

    <v-col cols="12">
      <v-chip
        v-for="fileName in localPhotos"
        :key="fileName"
        color="primary"
        size="small"
        class="me-2"
      >
        {{ fileName.name }}
      </v-chip>
    </v-col>

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
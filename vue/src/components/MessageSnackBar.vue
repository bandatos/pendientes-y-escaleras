<script setup>
import { watch } from "vue";

defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  text: {
    text: String,
    required: true,
    default: "",
  },
  timer: {
    type: String,
    default: "5000",
  },
  type: {
    type: String,
  },
});

const showSnackBar = ref(false);

watch(())

</script>
<template>
  <v-snackbar
    v-model="showSnackBar"
    :color="type"
    :timeout="timer != '0' && timer != '' ? timer : '-1'"
    elevation="10"
    :max-width="1000"
  >
    <template v-slot:action="{ attrs }">
      <v-btn
        light
        v-bind="attrs"
        @click="showSnackBar = false"
        class="text-caption"
      >
        <span v-if="type == 'success'">OK</span>
        <span v-else-if="type == 'warning'">ENTENDIDO</span>
        <span v-else>ACEPTAR</span>
      </v-btn>
    </template>
  </v-snackbar>
</template>
<style scoped>
</style>
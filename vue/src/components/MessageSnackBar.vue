<script setup>
import { computed } from 'vue'
import { useSnackbarStore } from '../stores/snackbarStore'
import { storeToRefs } from 'pinia'

const snackbarStore = useSnackbarStore()

// Usar refs del store para mantener reactividad
const { show, text, type, timeout } = storeToRefs(snackbarStore)

// Computed para manejar v-model
const showSnackbar = computed({
  get() {
    return show.value
  },
  set(value) {
    if (!value) {
      snackbarStore.close()
    }
  }
})

// Computed para determinar el texto del botón según el tipo
const buttonText = computed(() => {
  switch (type.value) {
    case 'success':
      return 'OK'
    case 'warning':
      return 'ENTENDIDO'
    case 'error':
      return 'CERRAR'
    default:
      return 'ACEPTAR'
  }
})
</script>
<template>
  <v-snackbar
    v-model="showSnackbar"
    :color="type"
    :timeout="timeout"
    elevation="10"
    :max-width="1000"
    location="top"
  >
    {{ text }}

    <template v-slot:actions>
      <v-btn
        variant="text"
        @click="showSnackbar = false"
        class="text-caption"
      >
        {{ buttonText }}
      </v-btn>
    </template>
  </v-snackbar>
</template>
<style scoped>
</style>
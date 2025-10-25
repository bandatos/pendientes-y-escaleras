import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSnackbarStore = defineStore('snackbar', () => {

  // Estado
  const show = ref(false)
  const text = ref('')
  const type = ref('info') // 'success' | 'error' | 'warning' | 'info'
  const timeout = ref(5000) // milisegundos, -1 para infinito

  // Mostrar mensaje de éxito
  function showSuccess(message, duration = 5000) {
    show.value = true
    text.value = message
    type.value = 'success'
    timeout.value = duration
  }

  // Mostrar mensaje de error
  function showError(message, duration = 5000) {
    show.value = true
    text.value = message
    type.value = 'error'
    timeout.value = duration
  }

  // Mostrar mensaje de advertencia
  function showWarning(message, duration = 5000) {
    show.value = true
    text.value = message
    type.value = 'warning'
    timeout.value = duration
  }

  // Mostrar mensaje informativo
  function showInfo(message, duration = 5000) {
    show.value = true
    text.value = message
    type.value = 'info'
    timeout.value = duration
  }

  // Mostrar mensaje genérico
  function showMessage(message, messageType = 'info', duration = 5000) {
    show.value = true
    text.value = message
    type.value = messageType
    timeout.value = duration
  }

  // Cerrar snackbar
  function close() {
    show.value = false
  }

  return {
    // Estado
    show,
    text,
    type,
    timeout,

    // Acciones
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showMessage,
    close
  }
})

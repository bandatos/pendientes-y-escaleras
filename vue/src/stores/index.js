import { createPinia } from 'pinia'

// Creación de pinia, para los stores
export const pinia = createPinia()

// Exportar stores para fácil acceso
export { useSyncStore } from './syncStore.js'
export { useImageStore } from './imageStore.js'
export { useStationStore } from './stationStore.js'
export { useSurveyStore } from './surveyStore.js'
export { useSnackbarStore } from './snackbarStore.js'

//Login
export { useAuthStore } from './authStore.js'
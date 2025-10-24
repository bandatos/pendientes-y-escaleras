import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services'
import { useSnackbarStore } from './snackbarStore.js'
import { LocalStorageService } from '../services/localStorage.js'

const SERVICE = authService;

export const useAuthStore = defineStore('auth', () => {

    // Estado
    const user = ref(null)
    const token = ref(null)
    const isLoading = ref(false)

    // Computed
    const isAuthenticated = computed(() => token.value !== null)

    // Actions
    async function login(email) {
        //Inicializar dentro de la función, ya que fuera es el estado global aún.
        const snackbarStore = useSnackbarStore();   

        let itemRequest = {
            email,
        }

        try {
            isLoading.value = true

            const response = await SERVICE.login(itemRequest)

            // Actualizar estado local
            token.value = response.token
            user.value = response.user

            snackbarStore.showSuccess('Autenticación exitosa')

            return { success: true, data: response }

        } catch (error) {
            //Call error message
            snackbarStore.showError(`Error al autenticarse: ${error.message || error}`);
            return { success: false, error }
        } finally {
            isLoading.value = false
        }
    }

    // Cargar sesión desde localStorage
    function loadSession() {
        const savedToken = LocalStorageService.getToken()
        const savedUser = LocalStorageService.getUser()

        if (savedToken && savedUser) {
            token.value = savedToken
            user.value = savedUser
        }
    }

    // Cerrar sesión
    function logout() {
        token.value = null
        user.value = null
        LocalStorageService.clearSession()
    }

    return {
        // State
        user,
        token,
        isLoading,

        // Computed
        isAuthenticated,

        // Actions
        login,
        loadSession,
        logout
    }
});

export default useAuthStore
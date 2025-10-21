import { defineStore } from 'pinia'
import { authService } from '../services'
import { useSnackbarStore } from './snackbarStore.js'

const SERVICE = authService;

export const useAuthStore = defineStore('auth', () => {

    //Actions
    function login(mail) {

        //Inicializar dentro de la función, ya que fuera es el estado global aún.
        const snackbarStore = useSnackbarStore();

        let itemRequest = {
            mail,
        }

        SERVICE.login(itemRequest)
            .then(response => {
                return response;
            }, error => {
                //Call error message
                snackbarStore.showError(`Error al autenticarse: ${error}`);
            }
            ).finally(() => {
            })
    }
    

    return {


        //Actions
        login
    }
});

export default useAuthStore
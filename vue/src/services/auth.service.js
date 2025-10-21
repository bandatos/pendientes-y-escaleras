import { LocalStorageService } from './localStorage.js'
const Storage = LocalStorageService;
/* Autenticación del login as user */
export const authService = {
    login,
}

function login(itemRequest) {
    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(itemRequest)
    }

    return fetch('login', requestOptions)
        .then(response => {
            // Status Code:


            // Add to the storage to keep it.
            Storage.saveToKen(response.token);
            Storage.saveUser(response.user);


            //Finally
            return response;
        });
}
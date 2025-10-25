import { config } from '../main.js'
import { LocalStorageService } from './localStorage.js'
const Storage = LocalStorageService;
/* Autenticación del login as user */
export const authService = {
    login,
}

async function login(itemRequest) {
    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(itemRequest)
    }

    try {
        const response = await fetch(`${config.API_URL}/api/login/`, requestOptions)

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        // Parse JSON response
        const data = await response.json()

        // Save to localStorage
        if (data.token) {
            LocalStorageService.saveToken(data.token)
        }

        if (data.email) {
            LocalStorageService.saveUser(data.email)
        }

        return data
    } catch (error) {
        console.error('Error en login:', error)
        throw error
    }
}
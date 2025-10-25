// import { config } from '../main.js'
import { config } from '@/config.js'

export const catalogsService = {
    getCatalogs,
}

async function getCatalogs() {
    const requestOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    }


    const response = await fetch(`${config.API_URL}api/catalogs/all`, requestOptions)

    // Validar status HTTP
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    // Parsear JSON 
    const data = await response.json()

    return data
}
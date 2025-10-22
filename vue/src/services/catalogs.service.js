import { config } from '../main.js'
export const catalogsService = {
    getCatalogs,
}

function getCatalogs(itemRequest) {
    const requestOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(itemRequest)
    }

    return fetch(`${config.API_URL}api/catalogs/all`, requestOptions)
        .then(response => {
            // Status Code:


            


            //Finally
            return response;
        });
}
import { LocalStorageService } from '../services/localStorage.js'
const storage = LocalStorageService;

export function isAuthValid() {
    const token = storage.getToken();
    return token !== null && token !== undefined;
}

export function authHeader(isFormData) {
    // return authorization header with jwt token

    if (isAuthValid()) {
        let token = storage.getToken();

        if (token) {
            if (!isFormData) {
                return {
                    'Authorization': 'Token ' + token,
                    'Content-Type': 'application/json'
                };
            } else {
                /* Si se manda argumento, entonces no es tipo JSON */
                return {
                    'Authorization': 'Token ' + token,
                };
            }
        } else {
            /* storage.logout(); */

            location.reload(true);
        }
    }
}
async function parseDocToB64(file) {
    let b64 = "";
    b64 = await transformToB64(file);
    return b64;
}

function transformToB64(file) {
    return new Promise((resolve, reject) => {
        // Validar que file es realmente un File object
        if (!file || !(file instanceof File)) {
            reject(new Error(`Expected File object, got: ${typeof file}`));
            return;
        }

        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () =>
            resolve(reader.result.replace("data:", "").replace(/^.+,/, ""));
        reader.onerror = (error) => reject(error);
    });
}

export {
    parseDocToB64
}
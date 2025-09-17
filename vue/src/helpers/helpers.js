async function parseDocToB64(file) {
    let b64 = "";
    b64 = await transformToB64(file);
    return b64;
}

function transformToB64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readerAsDataURL(file);
        reader.onload = () =>
            resolve(reader.result.replace("data:", "").replace(/^.+,/, ""));
        reader.onerror = (error) => reject(error);
    });
}

export {
    parseDocToB64
}
import { config } from '../main.js'

export const stairsService = {
  saveStair,
  uploadStairImages,
}


async function saveStair(stairData) {
  const requestOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(stairData)
  }

  const response = await fetch(`${config.API_URL}api/stairs/`, requestOptions)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const data = await response.json()
  return data
}


async function uploadStairImages(stairId, images) {
  // Crear FormData para enviar archivos
  const formData = new FormData()

  // Agregar el stairId
  formData.append('stair_id', stairId)

  // Agregar cada imagen
  images.forEach((image, index) => {
    formData.append(`image_${index}`, image, image.name)
  })

  const requestOptions = {
    method: 'POST',
    body: formData
  }

  const response = await fetch(`${config.API_URL}api/stairs/images/`, requestOptions)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const data = await response.json()
  return data
}

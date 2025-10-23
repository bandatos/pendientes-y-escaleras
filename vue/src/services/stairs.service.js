import { config } from '../main.js'
import { authHeader } from '../utils/helpers.js'

export const stairsService = {
  saveStair,
  uploadStairImages,
}


async function saveStair(stairData) {
  const requestOptions = {
    method: 'POST',
    headers: authHeader(), // false = JSON con Content-Type
    body: JSON.stringify(stairData)
  }

  const response = await fetch(`${config.API_URL}api/stair_report/`, requestOptions)

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const data = await response.json()
  return data
}


async function uploadStairImages(stair_id, images) {
  // Crear FormData para enviar archivos
  const formData = new FormData()

  // Agregar cada imagen
  images.forEach((image, index) => {
    formData.append(`image_${index}`, image, image.name)
  })

  const requestOptions = {
    method: 'POST',
    headers: authHeader(true), // true = FormData sin Content-Type
    body: formData
  }

  const response = await fetch(
    `${config.API_URL}api/stair_report/${stair_id}/evidence_image/`,
    requestOptions
  )

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const data = await response.json()
  return data
}

import requests

# Configuración
ACCESS_TOKEN = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_iE_XXyAtX2ONg_AlhzviAvnJte0"
BOARD_ID = "uXjVJucVbCE="

# Headers para la API
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json"
}

# Endpoint para obtener items del board (filtrado por tipo frame)
url = f"https://api.miro.com/v2/boards/{BOARD_ID}/items"

# Parámetros para filtrar solo frames
params = {
    "type": "frame",
    "limit": 10  # Máximo por página
}

# Hacer la petición
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    frames = data.get("data", [])

    print(f"Se encontraron {len(frames)} frames:\n")

    for frame in frames:
        print(f"ID: {frame['id']}")
        print(f"Título: {frame.get('data', { }).get('title', 'Sin título')}")
        print(f"Posición: x={frame['position']['x']}, y={frame['position']['y']}")
        print(f"Dimensiones: {frame['geometry']['width']} x {frame['geometry']['height']}")
        print("-" * 50)
else:
    print(f"Error {response.status_code}: {response.text}")
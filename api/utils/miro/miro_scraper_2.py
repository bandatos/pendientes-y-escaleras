import requests
import json

# Configuración
ACCESS_TOKEN = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_iE_XXyAtX2ONg_AlhzviAvnJte0"
BOARD_ID = "uXjVJucVbCE="

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json"
}

# Endpoint para obtener items del board (filtrado por tipo frame)
base_url = f"https://api.miro.com/v2/boards/{BOARD_ID}"
cursor = None
# Parámetros para filtrar solo frames
params = {
    "type": "frame",
    "limit": 50  # Máximo por página
}

find_name = "Mixcoac"
frame_id = '3458764661678874975'
# frame_id = '3458764647504710354'
found_frame = None


items_url = f"{base_url}/items"
while True:
    params["cursor"] = cursor
    response = requests.get(items_url, headers=headers, params=params)
    data = response.json()
    frames = data.get("data", [])
    for frame in frames:
        title = frame.get('data', {}).get('title', '')
        if find_name == title:
            found_frame = frame
            print(f"ID: {frame['id']}")
            print(f"Título: {title}")
            print(f"Posición: x={frame['position']['x']}, y={frame['position']['y']}")
            print(f"Dimensiones: {frame['geometry']['width']} x {frame['geometry']['height']}")
            print("-" * 50)
            break
    cursor = data.get("cursor")
    if not cursor:
        break


print("Frame encontrado:\n", found_frame)
if found_frame:
    json_data = json.dumps(found_frame, indent=4)
    link_data = found_frame.get('links', {}).get('self')
    if link_data:
        frame_items_url = f"{base_url}/items?parent_item_id={frame_id}"
        frame_items = {"limit": 50}
        frame_items_response = requests.get(
            frame_items_url, headers=headers, params=frame_items)
        if frame_items_response.status_code == 200:
            frame_items_data = frame_items_response.json()
            frame_items_json = json.dumps(frame_items_data, indent=4)
            # print("Contenido del frame:\n", json.dumps(content_data, indent=4))
        else:
            print(f"Error al obtener contenido del frame: "
                  f"{frame_items_response.status_code}"
                  f" - {frame_items_response.text}")

        frame_connectors_url = f"{base_url}/connectors?source_item_id={frame_id}"
        connectors_response = requests.get(
            frame_connectors_url, headers=headers, params={"limit": 50})
        if connectors_response.status_code == 200:
            connectors_data = connectors_response.json()
            connectors_json = json.dumps(connectors_data, indent=4)
            # print("Conectores del frame:\n", json.dumps(connectors_data, indent=4))
        else:
            print(f"Error al obtener conectores del frame: "
                  f"{connectors_response.status_code}"
                  f" - {connectors_response.text}")









# Hacer la petición
response = requests.get(base_url, headers=headers, params=params)

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


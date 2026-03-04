from django.conf import settings

import requests

ACCESS_TOKEN = settings.MIRO_ACCESS_TOKEN

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json"
}
base_url = f"https://api.miro.com/v2/boards/{settings.MIRO_BOARD_ID}"

def get_all_paginated(url: str, params: dict = None) -> list:
    params = params or {"limit": 50}
    results = []
    cursor = None

    while True:
        if cursor:
            params["cursor"] = cursor

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        results.extend(data.get("data", []))

        cursor = data.get("cursor")
        if not cursor:
            break

    return results

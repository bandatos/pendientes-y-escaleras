from .helpers import get_all_paginated, base_url, headers


all_connectors = []


def search_frame_by_title(title: str) -> dict | None:
    frames_url = f"{base_url}/items"
    params = {"limit": 50, "type": "frame"}
    frames = get_all_paginated(frames_url, params)

    for frame in frames:
        if frame.get('data', {}).get('title', '') == title:
            return frame

    return None


def get_frame_items(frame_id: str) -> list:
    items_url = f"{base_url}/items"
    params = {"limit": 50, "parent_item_id": frame_id}
    return get_all_paginated(items_url, params)


def get_connectors():
    global all_connectors
    if not all_connectors:
        connectors_url = f"{base_url}/connectors"
        all_connectors = get_all_paginated(connectors_url, {"limit": 50})
    return all_connectors


def get_frame_connectors(frame_id: str, frame_items: list | None = None) -> list:
    connectors = get_connectors()
    frame_connectors = []
    if not frame_items:
        frame_items = get_frame_items(frame_id)
    frame_item_ids = { item["id"] for item in frame_items }
    for conn in connectors:
        start_id = conn.get("startItem", {}).get("id")
        end_id = conn.get("endItem", {}).get("id")

        if start_id in frame_item_ids or end_id in frame_item_ids:
            frame_connectors.append(conn)
    return frame_connectors



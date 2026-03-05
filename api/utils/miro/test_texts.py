from utils.miro.helpers import get_all_paginated, base_url
import json
import re

_LINE_RE = re.compile(r'^(L\d{1,2}[AB]?)\b')
_LEVEL_TEXT_RE = re.compile(
    r'(L\d{1,2}[AB]?)\s+Nivel\s+(Andenes\s+)?([-\d]+|superficie\s+\d+)',
    re.IGNORECASE,
)

def _strip_html(html: str) -> str:
    text = re.sub(r'<br[^>]*/?>|<br>', ' ', html, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()


text_params = {
    # "type": "frame",
    "type": "text",
    "limit": 50  # Máximo por página
}

items_url = f"{base_url}/items"
all_texts_items = get_all_paginated(items_url, text_params)
all_contents = [text.get('data', {}).get('content', '')
                for text in all_texts_items]

raw_contents = [_strip_html(content) for content in all_contents]
unique_raw_contents = set(raw_contents)

for content in all_contents:
    raw = _strip_html(content)
    level_match = _LEVEL_TEXT_RE.search(raw)
    if not level_match:
        print(f"No se encontró nivel en: '{raw}'")
        continue





all_texts_items_json = json.dumps(all_texts_items, indent=4)


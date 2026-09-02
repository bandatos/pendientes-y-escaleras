"""Management command: vuelca en JSON el contenido crudo del tablero Miró."""
import json
import os
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand

from utils.miro.frames import get_all_frames, get_frame_items


class Command(BaseCommand):
    """Vuelca cada frame de Miró y el `data.content` de sus ítems a un JSON.

    Es de solo lectura: no toca la base ni el tablero. Sirve para auditar
    convenciones del tablero (marcas entre corchetes, títulos, rótulos de
    andén) sin gastar una llamada por consulta.

    Uso::

        python manage.py dump_miro_raw
        python manage.py dump_miro_raw --output /tmp/miro.json
    """

    help = (
        "Vuelca a JSON todos los frames de Miró con el contenido crudo "
        "de sus ítems. Solo lectura."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help=(
                "Ruta del JSON de salida. Por defecto: "
                "media/miro_previews/raw/miro_raw_<YYYYMMDD>.json."
            ),
        )

    def handle(self, *args, **options) -> None:
        output_path: str = options["output"] or self._default_output()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        frames = get_all_frames()
        self.stdout.write(f"Frames en Miró: {len(frames)}")

        payload = []
        for i, frame in enumerate(frames, 1):
            title = frame.get("data", {}).get("title", "")
            items = get_frame_items(frame["id"])
            payload.append({
                "frame_id": frame["id"],
                "title": title,
                "items": [
                    {
                        "id": item.get("id"),
                        "type": item.get("type"),
                        "shape": item.get("data", {}).get("shape"),
                        "content": item.get("data", {}).get("content", ""),
                        # El color de relleno codifica convenciones del
                        # tablero (accesos grises) que aún no se importan.
                        "style": item.get("style", {}),
                    }
                    for item in items
                ],
            })
            self.stdout.write(f"  {i}/{len(frames)} {title} ({len(items)})")

        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"JSON: {output_path}"))

    def _default_output(self) -> str:
        raw_dir = os.path.join(
            settings.BASE_DIR, "media", "miro_previews", "raw"
        )
        stamp = date.today().strftime("%Y%m%d")
        return os.path.join(raw_dir, f"miro_raw_{stamp}.json")

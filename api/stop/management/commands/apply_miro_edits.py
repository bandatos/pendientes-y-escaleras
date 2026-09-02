"""Management command: aplica al tablero de Miró un lote de correcciones."""
import json

import requests
from django.core.management.base import BaseCommand, CommandError

from utils.miro.helpers import base_url, headers

TIMEOUT = 30

# Campo que se corrige según el tipo de ítem: el texto de una forma o el
# título de un frame.
ENDPOINTS = {
    'shape': ('shapes', 'content'),
    'frame': ('frames', 'title'),
}


class Command(BaseCommand):
    """Aplica correcciones de texto y de título sobre el tablero de Miró.

    Lee la clave ``edits`` de un JSON con la forma::

        {"edits": [{"frame": str, "item_id": str, "item_type": "shape",
                    "current": str, "proposed": str,
                    "current_text": str, "proposed_text": str,
                    "reason": str}]}

    Las demás claves del archivo son diagnóstico y se ignoran. Hay un
    archivo de muestra en ``utils/miro/apply_miro_edits.example.json``.

    Uso::

        python manage.py apply_miro_edits --edits plan.json
        python manage.py apply_miro_edits --edits plan.json --apply
    """

    help = (
        "Aplica al tablero de Miró las correcciones de un JSON. "
        "Sin --apply solo imprime el plan, no manda ninguna petición."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--edits",
            type=str,
            required=True,
            help="Ruta del JSON con la clave 'edits'.",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Manda los PATCH; sin esta bandera solo simula.",
        )

    def handle(self, *args, **options) -> None:
        edits = self._load_edits(options["edits"])
        apply_changes: bool = options["apply"]

        session = requests.Session()
        session.headers.update(
            {**headers, "Content-Type": "application/json"})

        applied = skipped = failed = 0
        for edit in edits:
            self.stdout.write(
                f"\n{edit['frame']} / {edit['item_id']} "
                f"({edit['item_type']})\n"
                f"  - {edit['current_text']!r}\n"
                f"  + {edit['proposed_text']!r}\n"
                f"  motivo: {edit['reason']}"
            )
            if not apply_changes:
                continue

            # El tablero es compartido y se edita a mano: si el valor cambió
            # desde que se generó el plan, la corrección ya no aplica al
            # texto revisado y se aborta esa entrada, no todo el lote.
            try:
                live = self._fetch_current(session, edit)
            except requests.HTTPError as exc:
                self.stderr.write(f"  ERROR al releer: {exc}")
                failed += 1
                continue
            if live != edit["current"]:
                self.stdout.write(
                    "  OMITIDO: el valor en el tablero ya no coincide\n"
                    f"    tablero: {live!r}"
                )
                skipped += 1
                continue

            try:
                self._patch(session, edit)
            except requests.HTTPError as exc:
                self.stderr.write(f"  ERROR al aplicar: {exc}")
                failed += 1
                continue
            self.stdout.write(self.style.SUCCESS("  APLICADO"))
            applied += 1

        if not apply_changes:
            self.stdout.write(
                f"\nSIMULACIÓN: {len(edits)} cambios, ninguno enviado. "
                "Usa --apply para ejecutarlos."
            )
            return

        summary = (
            f"\naplicados={applied} omitidos={skipped} fallidos={failed}")
        if failed:
            raise CommandError(summary)
        self.stdout.write(self.style.SUCCESS(summary))

    def _load_edits(self, path: str) -> list[dict]:
        try:
            with open(path, encoding="utf-8") as fh:
                payload = json.load(fh)
        except OSError as exc:
            raise CommandError(f"No se pudo leer '{path}': {exc}")
        except json.JSONDecodeError as exc:
            raise CommandError(f"JSON inválido en '{path}': {exc}")

        edits = payload.get("edits")
        if not isinstance(edits, list):
            raise CommandError(
                f"'{path}' no tiene una lista en la clave 'edits'.")
        unknown = {
            e.get("item_type") for e in edits
        } - set(ENDPOINTS)
        if unknown:
            raise CommandError(f"item_type no soportado: {sorted(unknown)}")
        return edits

    @staticmethod
    def _item_url(edit: dict) -> str:
        collection, _ = ENDPOINTS[edit["item_type"]]
        return f"{base_url}/{collection}/{edit['item_id']}"

    def _fetch_current(
        self, session: requests.Session, edit: dict
    ) -> str:
        """Valor actual del campo en el tablero, tal como está ahora mismo."""
        _, key = ENDPOINTS[edit["item_type"]]
        resp = session.get(self._item_url(edit), timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json().get("data", {}).get(key, "")

    def _patch(self, session: requests.Session, edit: dict) -> None:
        _, key = ENDPOINTS[edit["item_type"]]
        resp = session.patch(
            self._item_url(edit),
            json={"data": {key: edit["proposed"]}},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()

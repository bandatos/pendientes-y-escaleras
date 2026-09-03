"""Management command: lee lo que se corrigió a mano en JOSM.

El .osm generado es una propuesta; el que vuelve de JOSM es la respuesta.
Este comando la traduce a metros del marco local de la plantilla, que es
donde la corrección se puede discutir y llevar de vuelta al JSON.
"""
from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from utils.osm.diff import (DiffError, compare, label, read_document,
                            read_frame)
from utils.osm.geometry import LocalFrame


class Command(BaseCommand):
    help = ("Compara el .osm generado con el que volvió editado de JOSM y "
            "reporta los cambios en metros del marco local.")

    def add_arguments(self, parser):
        parser.add_argument("generated")
        parser.add_argument("edited")
        parser.add_argument("--anchor",
                            help="LAT,LON si el generado no trae el marco.")
        parser.add_argument("--bearing", type=float)
        parser.add_argument("--mirror", action="store_true")
        parser.add_argument("--tags", action="store_true",
                            help="Detalla también los cambios de etiqueta.")

    def handle(self, *args, **opts):
        gen_path, edit_path = Path(opts["generated"]), Path(opts["edited"])
        for path in (gen_path, edit_path):
            if not path.exists():
                raise CommandError(f"no existe {path}")
        try:
            frame = self._frame(opts, gen_path)
            generated = read_document(gen_path, frame)
            edited = read_document(edit_path, frame)
        except DiffError as exc:
            raise CommandError(str(exc))

        result = compare(generated, edited)
        self.stdout.write(
            f"{gen_path.name} → {edit_path.name}  "
            f"(marco: ancla {frame.lat:.7f},{frame.lon:.7f}, rumbo "
            f"{frame.bearing_deg}°)")
        self.stdout.write(
            f"generado: {len(generated)} objetos; editado: {len(edited)}")

        self._section("movidos (du, dv en metros del marco)", [
            f"{label(el)}: du {du:+.2f}, dv {dv:+.2f} — {dist:.2f} m"
            for el, du, dv, dist in sorted(
                result["moved"], key=lambda t: -t[3])])
        self._section("reformados (cambió el número de vértices)", [
            f"{label(el)}: {before} → {after} nodos"
            for el, before, after in result["reshaped"]])
        self._section("borrados", [label(el)
                                   for el in result["deleted"]])
        self._section("añadidos en JOSM", [label(el)
                                           for el in result["added"]])
        changed = result["retagged"]
        if opts["tags"]:
            lines = []
            for el, changes in changed:
                lines.append(label(el))
                for key, old, new in changes:
                    lines.append(f"    {key}: {old or '—'} → {new or '—'}")
            self._section("etiquetas", lines, count=len(changed))
        else:
            self._section("etiquetas", [
                f"{label(el)}: " + ", ".join(k for k, _, _ in changes)
                for el, changes in changed])
            if changed:
                self.stdout.write("  (usa --tags para ver los valores)")

    def _frame(self, opts, gen_path) -> LocalFrame:
        if opts["anchor"]:
            try:
                lat_s, lon_s = opts["anchor"].split(",")
            except ValueError:
                raise CommandError("--anchor debe ser LAT,LON")
            if opts["bearing"] is None:
                raise CommandError("con --anchor hace falta --bearing")
            return LocalFrame(float(lat_s), float(lon_s), opts["bearing"],
                              mirror=opts["mirror"])
        return read_frame(gen_path)

    def _section(self, title: str, lines: list, count=None) -> None:
        total = len(lines) if count is None else count
        self.stdout.write("")
        self.stdout.write(f"{title}: {total}" if lines
                          else f"{title}: ninguno")
        for line in lines:
            self.stdout.write(f"  {line}")

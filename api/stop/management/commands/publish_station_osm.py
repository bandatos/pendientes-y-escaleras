"""Management command: copia de una versión aprobada lista para subir.

Escribe `<slug>-NN-pub.osm` junto a la versión: sin etiquetas de traza y
sin `upload='never'`. Queda fuera de la cadena de versiones (el autor
`pub` no cuenta al numerar) y nunca se sobrescribe.
"""
from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from utils.osm.publish import (PublishError, action_counts, pub_path,
                               strip_for_upload)


class Command(BaseCommand):
    help = ("Escribe la copia de publicación de una versión aprobada: sin "
            "note:* de traza ni upload='never'.")

    def add_arguments(self, parser):
        parser.add_argument("version", help="Ruta de la versión aprobada.")
        parser.add_argument("--out-dir",
                            help="Escribe la copia en otra carpeta.")

    def handle(self, *args, **opts):
        src = Path(opts["version"])
        if not src.is_file():
            raise CommandError(f"no existe {src}")
        try:
            out = pub_path(src)
            if opts["out_dir"]:
                out = Path(opts["out_dir"]) / out.name
            if out.exists():
                raise CommandError(f"ya existe {out}; no se sobrescribe")
            text = src.read_bytes().decode("utf-8")
            published, n_tags, had_upload = strip_for_upload(text)
            counts = action_counts(published)
        except PublishError as exc:
            raise CommandError(str(exc))

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(published.encode("utf-8"))
        self.stdout.write(f"{src.name} → {out}")
        self.stdout.write(f"etiquetas de traza quitadas: {n_tags}")
        self.stdout.write("upload quitado del <osm>" if had_upload
                          else "el <osm> no traía upload")
        for kind in ("node", "way", "relation"):
            bucket = counts.get(kind)
            if bucket:
                detail = ", ".join(f"{k} {n}" for k, n in
                                   sorted(bucket.items()))
                self.stdout.write(f"  {kind}: {detail}")
            else:
                self.stdout.write(f"  {kind}: ninguno nuevo ni con action")

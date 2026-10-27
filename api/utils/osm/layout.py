"""Rutas de la carpeta de una estación bajo data/osm.

Cada estación vive en `data/osm/<línea>-<slug>/` y cada turno de edición
es un archivo numerado `<slug>-NN-<autor>.osm`: el generador y Ricardo se
alternan sobre la misma estación y ninguno pisa la versión del otro.
"""
from __future__ import annotations

import re
from pathlib import Path

# Las líneas del Metro van en el stop_id de la estación: 0200L7-SANJOAQUIN.
_LINE_RE = re.compile(r"L([0-9A-Z]+)-")

# Autor de la copia de publicación: repite el número de su versión y no es
# un turno, así que contarla la volvería «la última».
PUB_AUTHOR = "pub"


class LayoutError(ValueError):
    pass


def line_code(stop_id: str) -> str:
    m = _LINE_RE.search(stop_id or "")
    if not m:
        raise LayoutError(
            f"no se puede leer la línea del stop_id «{stop_id}»; "
            "usa --out")
    return f"l{m.group(1).lower()}"


def station_dir(osm_dir: Path, stop_id: str, slug: str) -> Path:
    return osm_dir / f"{line_code(stop_id)}-{slug}"


def _versions(folder: Path, slug: str) -> list[tuple[int, Path]]:
    version_re = re.compile(rf"{re.escape(slug)}-(\d{{2}})-([a-z]+)\.osm")
    return [(int(m.group(1)), p) for p in folder.glob("*.osm")
            if (m := version_re.fullmatch(p.name))
            and m.group(2) != PUB_AUTHOR]


def next_version_path(folder: Path, slug: str,
                      author: str = "claude") -> Path:
    """Siguiente número libre, sea quien sea el autor del último turno."""
    numbers = [n for n, _ in _versions(folder, slug)]
    return folder / f"{slug}-{max(numbers, default=0) + 1:02d}-{author}.osm"


def latest_version_path(folder: Path | None, slug: str) -> Path | None:
    """La versión de NN más alto, sea quien sea su autor."""
    if folder is None:
        return None
    found = _versions(folder, slug)
    return max(found)[1] if found else None

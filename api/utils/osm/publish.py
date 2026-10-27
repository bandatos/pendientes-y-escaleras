"""Copia de publicación de una versión aprobada.

La versión aprobada puede venir editada a mano en JOSM, así que regenerar
con `--no-trace` no sirve: se quitan las etiquetas de traza y el bloqueo
de subida sobre el texto mismo, sin reescribir el XML, para que el archivo
que se sube sea el que se revisó salvo esas dos cosas.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from . import tags as T
from .layout import PUB_AUTHOR

_VERSION_RE = re.compile(
    r"(?P<slug>.+)-(?P<nn>\d{2})-(?P<author>[a-z]+)\.osm")
_KEYS = "|".join(re.escape(k) for k in T.TRACE_KEYS)
_TAG = rf"<tag\s[^>]*?k=(['\"])(?:{_KEYS})\1[^>]*?/>"
# Línea entera primero, con su fin de línea tal cual (JOSM guarda en CRLF);
# después las que comparten línea con otro elemento.
_TAG_LINE_RE = re.compile(rf"^[ \t]*{_TAG}[ \t]*(?:\r\n|\n|\r)?", re.M)
_TAG_INLINE_RE = re.compile(_TAG)
_UPLOAD_RE = re.compile(r"(<osm\b[^>]*?)\s+upload=(['\"])[^'\"]*\2")


class PublishError(ValueError):
    pass


def pub_path(src: Path) -> Path:
    m = _VERSION_RE.fullmatch(src.name)
    if not m:
        raise PublishError(
            f"«{src.name}» no es una versión <slug>-NN-<autor>.osm")
    if m.group("author") == PUB_AUTHOR:
        raise PublishError(f"«{src.name}» ya es una copia de publicación")
    return src.with_name(f"{m.group('slug')}-{m.group('nn')}-"
                         f"{PUB_AUTHOR}.osm")


def strip_for_upload(text: str) -> tuple[str, int, bool]:
    """Texto sin traza ni `upload`; cuántas etiquetas y si había bloqueo."""
    out, n_lines = _TAG_LINE_RE.subn("", text)
    out, n_inline = _TAG_INLINE_RE.subn("", out)
    out, n_upload = _UPLOAD_RE.subn(r"\1", out, count=1)
    return out, n_lines + n_inline, bool(n_upload)


def action_counts(text: str) -> dict[str, Counter]:
    """Por tipo de elemento: nuevos (id negativo) y cada `action`.

    También comprueba que el resultado siga siendo XML y que no quede
    traza, para no entregar a la subida un archivo roto.
    """
    root = ET.fromstring(text.encode("utf-8"))
    if root.get("upload") is not None:
        raise PublishError("el <osm> conserva el atributo upload")
    counts: dict[str, Counter] = {}
    for el in root:
        if el.tag not in ("node", "way", "relation"):
            continue
        left = [t.get("k") for t in el.iter("tag")
                if t.get("k") in T.TRACE_KEYS]
        if left:
            raise PublishError(
                f"{el.tag} {el.get('id')} conserva {', '.join(left)}")
        bucket = counts.setdefault(el.tag, Counter())
        if int(el.get("id")) < 0:
            bucket["nuevo"] += 1
        if el.get("action"):
            bucket[el.get("action")] += 1
    return counts

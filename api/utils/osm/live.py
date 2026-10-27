"""Contraste de una versión de estación con el estado vivo de OSM.

Antes de subir hay que saber tres cosas que el archivo no sabe: si
alguien editó en OSM lo que vamos a modificar o borrar (conflicto de
versión), si un nodo que damos de baja sigue en alguna vía o relación
del servidor (la subida fallaría) y si lo que tocamos pertenece a
relaciones que no viajan en el archivo. Se consulta la API 0.6 y no
Overpass porque solo la API da la versión vigente sin retraso.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .overpass import USER_AGENT

API = "https://api.openstreetmap.org/api/0.6"
BATCH = 100
KINDS = ("node", "way", "relation")


class LiveCheckError(Exception):
    pass


@dataclass
class FileElement:
    kind: str
    id: int
    action: str | None
    version: int | None
    refs: set[tuple[str, int]] = field(default_factory=set)


@dataclass
class LiveReport:
    checked: int = 0
    conflicts: list[str] = field(default_factory=list)
    gone: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    missing_relations: list[str] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        return bool(self.conflicts or self.gone or self.blocked)


def read_file(path: Path) -> dict[tuple[str, int], FileElement]:
    """Elementos del archivo con su acción, versión y referencias.

    Con ElementTree y no con `OsmDocument`: el documento no se carga de
    un archivo y aquí solo hacen falta ids, versiones y referencias.
    """
    out = {}
    for elem in ET.parse(path).getroot():
        if elem.tag not in KINDS:
            continue
        version = elem.get("version")
        item = FileElement(elem.tag, int(elem.get("id")), elem.get("action"),
                           int(version) if version else None)
        for nd in elem.findall("nd"):
            item.refs.add(("node", int(nd.get("ref"))))
        for m in elem.findall("member"):
            item.refs.add((m.get("type"), int(m.get("ref"))))
        out[(item.kind, item.id)] = item
    return out


def http_get_json(url: str) -> dict | None:
    """GET a la API; None si el elemento no existe (404) o se borró (410)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 410):
            return None
        raise LiveCheckError(f"{url}: HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise LiveCheckError(f"{url}: {exc}") from exc


Getter = Callable[[str], "dict | None"]


def server_versions(kind: str, ids: list[int], get: Getter
                    ) -> dict[int, tuple[int, bool] | None]:
    """{id: (versión, visible)}; None si el servidor no lo tiene.

    La consulta múltiple falla entera si un id no existe, así que ese
    lote se repite elemento por elemento.
    """
    out: dict[int, tuple[int, bool] | None] = {}
    for start in range(0, len(ids), BATCH):
        chunk = ids[start:start + BATCH]
        joined = ",".join(str(i) for i in chunk)
        data = get(f"{API}/{kind}s.json?{kind}s={joined}")
        if data is None:
            for i in chunk:
                one = get(f"{API}/{kind}/{i}.json")
                out[i] = _first_version(one)
            continue
        for e in data.get("elements", []):
            out[e["id"]] = (e["version"], e.get("visible", True))
        for i in chunk:
            out.setdefault(i, None)
    return out


def _first_version(data):
    if not data or not data.get("elements"):
        return None
    e = data["elements"][0]
    return e["version"], e.get("visible", True)


def referrers(kind: str, eid: int, get: Getter) -> set[tuple[str, int]]:
    """Ways y relaciones del servidor que hoy contienen al elemento."""
    paths = [("relation", "relations")]
    if kind == "node":
        paths.insert(0, ("way", "ways"))
    out = set()
    for parent, suffix in paths:
        data = get(f"{API}/{kind}/{eid}/{suffix}.json") or {}
        for e in data.get("elements", []):
            out.add((parent, e["id"]))
    return out


def check(elements: dict[tuple[str, int], FileElement], get: Getter
          ) -> LiveReport:
    report = LiveReport()
    touched = [e for e in elements.values()
               if e.id > 0 and e.action in ("modify", "delete")]
    report.checked = len(touched)
    for kind in KINDS:
        mine = sorted(e.id for e in touched if e.kind == kind)
        if not mine:
            continue
        live = server_versions(kind, mine, get)
        for eid in mine:
            local = elements[(kind, eid)]
            found = live.get(eid)
            if found is None or not found[1]:
                report.gone.append(
                    f"{kind} {eid}: no existe o ya está borrado en OSM")
            elif found[0] != local.version:
                report.conflicts.append(
                    f"{kind} {eid}: el archivo trae v{local.version}, OSM "
                    f"está en v{found[0]}")
    for item in sorted(touched, key=lambda e: (KINDS.index(e.kind), e.id)):
        parents = referrers(item.kind, item.id, get)
        for pkind, pid in sorted(parents):
            if pkind == "relation" and (pkind, pid) not in elements:
                report.missing_relations.append(
                    f"{item.kind} {item.id} ({item.action}) es miembro de "
                    f"la relación {pid}, que no viaja en el archivo")
            if item.action == "delete" and _blocks(
                    elements.get((pkind, pid)), item):
                report.blocked.append(
                    f"{item.kind} {item.id} sale de baja pero el {pkind} "
                    f"{pid} de OSM lo sigue usando")
    return report


def _blocks(parent: FileElement | None, item: FileElement) -> bool:
    """¿Impide el padre del servidor la baja de `item`?

    Si el padre viaja en el archivo, la subida lo reescribe antes: solo
    bloquea si sale sin `delete` y todavía referencia al elemento.
    """
    if parent is None:
        return True
    if parent.action == "delete":
        return False
    return (item.kind, item.id) in parent.refs

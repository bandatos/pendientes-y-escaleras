"""Nodo compartido donde un way de su nivel cruza el anillo del andén."""
from .builder import StationBuilder
from .document import OsmDocument
from .geometry import LocalFrame
from .validate import _check_platform_crossings

SQUARE = [(0, 0), (10, 0), (10, 10), (0, 10)]


def _doc():
    doc = OsmDocument(LocalFrame(19.4, -99.1, 0.0))
    platform = doc.add_way(SQUARE, {"railway": "platform", "area": "yes",
                                    "level": "-3"},
                           [-3], kind="platform", label="andén",
                           closed=True)
    return doc, platform


def _footway(doc, points, level="-3"):
    return doc.add_way(points, {"highway": "footway", "level": level},
                       [int(p) for p in level.split(";")], label="pasillo")


def _join(doc):
    # El constructor pide grafo y plantilla; el método solo usa estos
    # tres atributos, así que se arma el builder sin `__init__`.
    builder = StationBuilder.__new__(StationBuilder)
    builder.doc = doc
    builder.warnings = []
    builder.report = {"platforms": []}
    builder._join_platform_crossings()
    return builder


def test_crossing_gets_a_new_node_on_both_segments():
    doc, platform = _doc()
    way = _footway(doc, [(5, -5), (5, 5)])
    before = set(doc.nodes)
    _join(doc)
    new = set(doc.nodes) - before
    assert len(new) == 1
    nid = new.pop()
    node = doc.nodes[nid]
    assert (round(node.u, 6), round(node.v, 6)) == (5, 0)
    # Entre (0, 0) y (10, 0) del anillo, entre las dos puntas del pasillo.
    assert platform.nodes.index(nid) == 1
    assert way.nodes.index(nid) == 1


def test_nearby_way_vertex_is_reused():
    doc, platform = _doc()
    way = _footway(doc, [(5, -5), (5, 0.2), (5, 5)])
    near = way.nodes[1]
    before = set(doc.nodes)
    _join(doc)
    assert set(doc.nodes) == before
    assert near in platform.nodes
    assert platform.nodes.index(near) == 1


def test_other_levels_are_not_joined():
    doc, platform = _doc()
    _footway(doc, [(3, -5), (3, 5)], level="-4")
    doc.add_way([(7, -5), (7, 5)], {"highway": "steps", "level": "-4;-3"},
                [-4, -3], label="escalera")
    ring = list(platform.nodes)
    before = set(doc.nodes)
    builder = _join(doc)
    assert set(doc.nodes) == before
    assert platform.nodes == ring
    assert builder.warnings == []
    assert builder.report["platforms"] == []
    assert _check_platform_crossings(doc) == []


def test_validator_warns_only_without_shared_node():
    doc, _ = _doc()
    _footway(doc, [(5, -5), (5, 5)])
    assert len(_check_platform_crossings(doc)) == 1
    _join(doc)
    assert _check_platform_crossings(doc) == []

"""Bajas de nodos de OSM al reformar un way ajeno."""
from types import SimpleNamespace

from .document import OsmDocument
from .geometry import LocalFrame

FRAME = LocalFrame(19.4, -99.1, 0.0)


def _foreign_node(osm_id: int, u: float, v: float):
    lat, lon = FRAME.to_wgs84(u, v)
    return SimpleNamespace(osm_id=osm_id, lat=lat, lon=lon, tags={},
                           meta={"version": "1"})


def _foreign_way(osm_id: int, node_ids, tags: dict):
    return SimpleNamespace(osm_id=osm_id, node_ids=list(node_ids),
                           tags=tags, meta={"version": "1"})


def test_context_embedded_after_reshape_keeps_shared_vertex():
    """Orden del builder: el contorno se reforma y la vía llega después.

    El vértice 2 del contorno de OSM lo comparte una vía; el 3 solo lo
    usa el contorno. Al final el 3 sale de baja y el 2 no, porque la vía
    viaja intacta en el archivo.
    """
    nodes = {1: _foreign_node(1, 0, 0), 2: _foreign_node(2, 10, 0),
             3: _foreign_node(3, 10, 10), 4: _foreign_node(4, 30, 0)}
    context = SimpleNamespace(nodes=nodes)
    doc = OsmDocument(FRAME)
    outline = doc.add_foreign_way(
        _foreign_way(100, [1, 2, 3, 1], {"public_transport": "station"}),
        context)
    ring = [doc.node_at(0, 1), doc.node_at(5, 1), doc.node_at(5, 5)]
    doc.adopt_way(outline, {}, ring)
    track = doc.add_foreign_way(
        _foreign_way(200, [2, 4], {"railway": "subway"}), context)

    doc.settle_deletes()

    assert track.nodes == [2, 4]
    assert doc.nodes[2].action is None
    assert doc.nodes[3].action == "delete"
    assert doc.nodes[1].action == "delete"

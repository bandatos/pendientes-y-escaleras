"""Soldadura alrededor de las puntas de escaleras de banco."""
import pytest

from .document import OsmDocument
from .geometry import LocalFrame
from .validate import _check_bank_tips


@pytest.fixture
def scene():
    """Footway con la punta de una escalera de banco a 0.2 m."""
    doc = OsmDocument(LocalFrame(19.4, -99.1, 0.0))
    footway = doc.add_way([(0, 0), (10, 0)],
                          {"highway": "footway", "level": "-2"}, [-2],
                          label="pasillo")
    short = doc.add_way([(5, -3), (5, -0.2)],
                        {"highway": "footway", "level": "-2"}, [-2],
                        label="tramo corto")
    doc.add_way([(5, -0.2), (5, -8)],
                {"highway": "steps", "level": "-2;-3"}, [-2, -3],
                label="escalera")
    return doc, footway, short.nodes[-1]


def test_weld_skips_bank_tip(scene):
    doc, footway, tip = scene
    doc.bank_tips.add(tip)
    doc.weld()
    assert len(footway.nodes) == 2
    assert tip not in footway.nodes


def test_weld_inserts_tip_when_not_marked(scene):
    doc, footway, tip = scene
    doc.weld()
    assert tip in footway.nodes[1:-1]


def test_check_bank_tips_flags_footway(scene):
    doc, footway, tip = scene
    doc.bank_tips.add(tip)
    footway.nodes.insert(1, tip)
    warnings = _check_bank_tips(doc)
    assert len(warnings) == 1
    assert f"footway {footway.id}" in warnings[0]

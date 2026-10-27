"""Sentido de dibujo de las escaleras eléctricas reversibles."""
from . import tags as T
from .document import OsmDocument
from .geometry import LocalFrame
from .validate import (_check_incline, _check_incline_order,
                       _check_reversible_sense)


def _tags(mode, bidirectional, lf, lt, runs="down"):
    reverse = T.draws_reversed(mode, bidirectional, lf, lt, runs)
    return reverse, T.way_tags_for_pathway(mode, bidirectional, lf, lt,
                                           reverse)


def test_reversible_drawn_downwards_whatever_the_pathway_sense():
    for lf, lt in ((-2, -1), (-1, -2)):
        reverse, tags = _tags(T.MODE_ESCALATOR, True, lf, lt)
        first = lt if reverse else lf
        assert first == -1
        assert tags["incline"] == "down"
        assert tags["conveying"] == "reversible"
        assert "oneway:foot" not in tags


def test_fixed_and_one_way_keep_their_sense():
    reverse, tags = _tags(T.MODE_STAIRS, True, -1, -2)
    assert reverse and tags["incline"] == "up"
    reverse, tags = _tags(T.MODE_ESCALATOR, False, -2, -1)
    assert not reverse and tags["incline"] == "up"
    assert tags["conveying"] == "forward"
    reverse, tags = _tags(T.MODE_ESCALATOR, True, -2, -1, runs="up")
    assert not reverse and tags["incline"] == "up"


def _scene(start_level, end_level, incline):
    """Reversible entre dos tramos cortos que fijan el nivel de sus puntas."""
    doc = OsmDocument(LocalFrame(19.4, -99.1, 0.0))
    doc.add_way([(0, -2), (0, 0)], {"highway": "footway",
                                    "level": str(start_level)},
                [start_level], label="tramo de arriba")
    doc.add_way([(0, 10), (0, 12)], {"highway": "footway",
                                     "level": str(end_level)},
                [end_level], label="tramo de abajo")
    lo, hi = sorted((start_level, end_level))
    doc.add_way([(0, 0), (0, 10)],
                {"highway": "steps", "level": f"{lo};{hi}",
                 "incline": incline, "conveying": "reversible"},
                [start_level, end_level], label="reversible")
    return doc


def test_validator_accepts_coherent_downward_reversible():
    doc = _scene(-1, -2, "down")
    assert _check_incline(doc) == []
    assert _check_incline_order(doc) == []
    assert _check_reversible_sense(doc) == []


def test_validator_flags_incoherent_and_old_convention():
    doc = _scene(-1, -2, "up")
    assert len(_check_incline_order(doc)) == 1
    doc = _scene(-2, -1, "up")
    assert _check_incline_order(doc) == []
    assert len(_check_reversible_sense(doc)) == 1

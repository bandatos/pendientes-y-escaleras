"""Descanso plano entre dos tramos de escalera."""
from .document import OsmDocument
from .geometry import LocalFrame
from .validate import _check_incline

STEPS = {"highway": "steps", "level": "-1;0", "incline": "up"}
LANDING = {"highway": "footway", "level": "-1;0"}


def _scene(second_run_levels="-1;0"):
    """Tramo, descanso, tramo: el acceso oriente de San Antonio."""
    doc = OsmDocument(LocalFrame(19.4, -99.1, 0.0))
    doc.add_way([(0, 0), (0, 4)], STEPS, [-1, 0], label="tramo 1")
    landing = doc.add_way([(0, 4), (0, 6)], LANDING, [-1, 0],
                          label="descanso")
    doc.add_way([(0, 6), (0, 10)],
                {**STEPS, "level": second_run_levels},
                [float(x) for x in second_run_levels.split(";")],
                label="tramo 2")
    return doc, landing


def test_landing_between_two_runs_needs_no_incline():
    doc, _ = _scene()
    assert _check_incline(doc) == []


def test_two_level_footway_without_runs_on_both_ends_still_flagged():
    doc, landing = _scene(second_run_levels="-2;-1")
    assert _check_incline(doc) == [
        f"way {landing.id}: cambia de nivel y no trae incline"]
    doc = OsmDocument(LocalFrame(19.4, -99.1, 0.0))
    doc.add_way([(0, 0), (0, 4)], STEPS, [-1, 0], label="tramo")
    loose = doc.add_way([(0, 4), (0, 6)], LANDING, [-1, 0],
                        label="pasillo")
    assert _check_incline(doc) == [
        f"way {loose.id}: cambia de nivel y no trae incline"]

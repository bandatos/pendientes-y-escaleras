"""Brazos y lóbulos medidos en el área, sin base de datos."""
from utils.osm.arms import measure_arms, resolve_arm_refs

# Franja de v -6 a 6 y u -80 a 80; brazo oriente de u -15 a -10 que
# abre en un lóbulo de u -23 a -9 (v 29 a 49); brazo poniente de u 5 a 9
# que abre en un lóbulo de u 5 a 15 (v -35 a -60). Los brazos no son
# colineales, como en General Anaya.
RING = [
    (-80, -6), (5, -6), (5, -60), (15, -60), (15, -35), (9, -35),
    (9, -6), (80, -6), (80, 6), (-10, 6), (-10, 29), (-9, 29),
    (-9, 49), (-23, 49), (-23, 29), (-15, 29), (-15, 6), (-80, 6),
]
BAND = (-6.0, 6.0)


def test_measure_arms_reads_axes_walls_and_doors():
    arms = measure_arms(RING, BAND)
    east, west = arms["+v"], arms["-v"]
    assert abs(east.axis_u - -12.5) < 1e-6
    assert abs(west.axis_u - 7.0) < 1e-6
    assert abs(east.wall_v - 49) < 1e-6 and abs(west.wall_v - -60) < 1e-6
    assert abs(east.face_v - 29) < 0.05 and abs(west.face_v - -35) < 0.05
    # La puerta va en el medio del tramo más largo de la cara fuera del
    # brazo, y sobre el anillo.
    assert abs(east.door[0] - -19.0) < 1e-6 and abs(east.door[1] - 29) < 1e-6
    assert abs(west.door[0] - 12.0) < 1e-6 and abs(west.door[1] - -35) < 1e-6


def test_resolve_arm_refs_fills_numbers_points_and_doors():
    data = {
        "station_node": {"u": {"arm": "mid"}},
        "nodes": {"E-01": {"locate": {"arm": "-v", "at": "door"}},
                  "N-03": {"u": {"arm": "-v"}, "v": -26.0}},
        "banks": {"b": {"junction": {"arm": "-v", "at": "wall",
                                     "inset": 3}}},
        "edges": [{"geometry": [
            "N-05", {"arm": "+v", "at": "wall", "inset": 3, "u": "door"},
            {"spine": "P-01", "u": {"arm": "+v", "du": 1.0}}]}],
    }
    out, doors = resolve_arm_refs(data, measure_arms(RING, BAND))
    assert doors == ["E-01"]
    assert abs(out["station_node"]["u"] - (-12.5 + 7.0) / 2) < 1e-6
    assert out["nodes"]["E-01"]["u"] == 12.0
    assert "locate" not in out["nodes"]["E-01"]
    assert out["nodes"]["N-03"]["u"] == 7.0
    assert out["banks"]["b"]["junction"] == [7.0, -57.0]
    geometry = out["edges"][0]["geometry"]
    assert geometry[1] == [-19.0, 46.0]
    assert geometry[2]["u"] == -11.5

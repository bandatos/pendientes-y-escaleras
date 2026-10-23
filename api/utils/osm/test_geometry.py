"""Pellizcos del KML: un solo anillo que en realidad encierra una isla."""
import pytest

from .geometry import (point_in_polygon, polygon_signed_area,
                       ring_self_intersections, split_pinched_ring)

# Franja de 40 × 6 m con un corredor en lazo del lado +v: patas en u 10–14
# y 26–30, travesaño en v 12–16, isla de 12 × 6 m en u 14–26, v 6–12. El
# anillo vuelve de la isla por el borde de la franja con dos vértices a
# 0.05 m de él: el corte de ancho cero que dibuja el KML de la L7.
PINCHED = [(0, 0), (40, 0), (40, 6), (30, 6), (30, 16), (10, 16), (10, 6),
           (14, 6), (14, 12), (26, 12), (26, 6), (15, 5.95), (9, 5.95),
           (0, 6)]
ISLAND_AREA_M2 = 12 * 6


def test_split_pinched_ring_turns_seam_into_island():
    rings, pinches = split_pinched_ring(PINCHED)

    outer, *inners = rings
    assert len(inners) == 1
    assert pinches
    assert abs(polygon_signed_area(inners[0])) == pytest.approx(
        ISLAND_AREA_M2, abs=1.0)
    assert all(not ring_self_intersections(r) for r in rings)
    assert not point_in_polygon([outer, *inners], (20, 9))
    assert point_in_polygon([outer, *inners], (20, 3))


def test_split_pinched_ring_leaves_clean_ring_alone():
    ring = [(0, 0), (40, 0), (40, 6), (0, 6)]

    rings, pinches = split_pinched_ring(ring)

    assert rings == [ring]
    assert pinches == []

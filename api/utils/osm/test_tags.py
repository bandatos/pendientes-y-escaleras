"""`layer` de los ways subterráneos de circulación."""
from . import tags as T


def test_footway_layer_only_below_ground():
    assert T.footway_tags([-2.0])["layer"] == "-2"
    assert "layer" not in T.footway_tags([0.0])
    assert "layer" not in T.connector_tags()


def test_steps_layer_is_the_lowest_level():
    assert T.steps_tags([-1.0, 0.0], "up")["layer"] == "-1"
    assert T.steps_tags([-2.0, -1.0], "up")["layer"] == "-2"


def test_platform_spine_layer():
    assert T.platform_spine_tags(-3)["layer"] == "-3"


def test_l7_reversible_keeps_indoor_and_level():
    reverse = T.draws_reversed(T.MODE_ESCALATOR, True, -1, 0)
    tags = T.way_tags_for_pathway(T.MODE_ESCALATOR, True, -1, 0, reverse)
    assert tags["layer"] == "-1"
    assert tags["indoor"] == "yes"
    assert tags["level"] == "-1;0"

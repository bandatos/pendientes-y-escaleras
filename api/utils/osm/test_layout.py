"""Rutas de la carpeta de una estación y numeración de versiones."""
import pytest

from .layout import latest_version_path, line_code, next_version_path


@pytest.mark.parametrize("stop_id, code", [
    ("0200L7-SANJOAQUIN", "l7"),
    ("020L12-TLAHUAC", "l12"),
    ("0200LB-BUENAVISTA", "lb"),
])
def test_line_code(stop_id, code):
    assert line_code(stop_id) == code


def test_next_version_starts_at_01(tmp_path):
    path = next_version_path(tmp_path, "portales")
    assert path.name == "portales-01-claude.osm"


def test_next_version_ignores_author_and_other_slugs(tmp_path):
    for name in ("portales-01-claude.osm", "portales-02-rick.osm",
                 "portales-03-rick.osm", "ermita-07-claude.osm"):
        (tmp_path / name).touch()
    path = next_version_path(tmp_path, "portales")
    assert path.name == "portales-04-claude.osm"


def test_latest_version_is_highest_number_any_author(tmp_path):
    for name in ("portales-01-claude.osm", "portales-03-rick.osm",
                 "portales-02-claude.osm", "ermita-07-claude.osm",
                 "portales.osm"):
        (tmp_path / name).touch()
    path = latest_version_path(tmp_path, "portales")
    assert path.name == "portales-03-rick.osm"

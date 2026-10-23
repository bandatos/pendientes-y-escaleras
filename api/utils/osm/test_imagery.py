"""Lectura de .osm y proyección para los compuestos satelitales."""
import pytest

from .imagery import load_osm, osm_frame, world_latlon, world_px

GENERATED = """<?xml version='1.0' encoding='UTF-8'?>
<osm version='0.6' generator='pendientes-y-escaleras' upload='never'>
  <!-- frame anchor=19.3914395,-99.1858392 bearing=6.5 mirror=true -->
</osm>
"""

JOSM = """<?xml version='1.0' encoding='UTF-8'?>
<osm version='0.6' upload='never' generator='JOSM'>
  <bounds minlat='19.39' minlon='-99.19' maxlat='19.40' maxlon='-99.18' />
</osm>
"""

EDITED = """<?xml version='1.0' encoding='UTF-8'?>
<osm version='0.6' generator='JOSM'>
  <node id='-1' lat='19.0' lon='-99.0' />
  <node id='-2' lat='19.1' lon='-99.1' />
  <node id='10' lat='19.2' lon='-99.2' version='1' />
  <node id='11' lat='19.3' lon='-99.3' version='1' />
  <way id='-5'><nd ref='-1' /><nd ref='-2' />
    <tag k='highway' v='footway' /></way>
  <way id='20' action='modify' version='1'><nd ref='10' /><nd ref='11' />
    <tag k='highway' v='steps' /></way>
  <way id='21' version='1'><nd ref='10' /><nd ref='11' />
    <tag k='highway' v='service' /></way>
  <way id='-6' action='delete'><nd ref='-1' /><nd ref='-2' />
    <tag k='highway' v='corridor' /></way>
</osm>
"""


def _write(tmp_path, text):
    path = tmp_path / "x.osm"
    path.write_text(text, encoding="utf-8")
    return path


def test_osm_frame_reads_generator_header(tmp_path):
    frame = osm_frame(_write(tmp_path, GENERATED))
    assert frame == (19.3914395, -99.1858392, 6.5, True)


def test_osm_frame_none_after_josm_save(tmp_path):
    assert osm_frame(_write(tmp_path, JOSM)) is None


def test_load_osm_keeps_own_and_modified_ways(tmp_path):
    _, ways, _ = load_osm(_write(tmp_path, EDITED))

    kinds = sorted(tags["highway"] for _, tags in ways)
    assert kinds == ["footway", "steps"]


@pytest.mark.parametrize("lat, lon", [(19.3914, -99.1858), (-33.9, 151.2)])
def test_world_px_round_trip(lat, lon):
    back = world_latlon(*world_px(lat, lon, 19), 19)
    assert back == pytest.approx((lat, lon), abs=1e-6)

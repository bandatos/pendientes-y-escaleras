"""Copia de publicación de una versión aprobada."""
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from .layout import latest_version_path, next_version_path

# Como lo guarda JOSM: CRLF, comillas simples, traza en ways y nodos.
APPROVED = (
    "<?xml version='1.0' encoding='UTF-8'?>\r\n"
    "<osm version='0.6' upload='never' generator='JOSM'>\r\n"
    "  <node id='-1' lat='19.4' lon='-99.1'>\r\n"
    "    <tag k='note:stop_id' v='L7-POLANCO-N-01' />\r\n"
    "    <tag k='railway' v='subway_entrance' />\r\n"
    "  </node>\r\n"
    "  <node id='42' action='modify' version='3' lat='19.4' lon='-99.2'>"
    "<tag k='note:miro_id' v='3458' /></node>\r\n"
    "  <node id='43' action='delete' version='1' lat='19.5' lon='-99.2' />"
    "\r\n"
    "  <way id='-2'>\r\n"
    "    <nd ref='-1' />\r\n"
    "    <nd ref='42' />\r\n"
    "    <tag k='highway' v='footway' />\r\n"
    "    <tag k='note' v='se conserva' />\r\n"
    "    <tag k='note:pathway_id' v='L7-POLANCO-P-07' />\r\n"
    "  </way>\r\n"
    "</osm>\r\n")


def test_publish_strips_trace_and_upload_only(tmp_path, capsys):
    src = tmp_path / "polanco-06-claude.osm"
    src.write_bytes(APPROVED.encode("utf-8"))

    call_command("publish_station_osm", str(src))

    pub = tmp_path / "polanco-06-pub.osm"
    expected = (APPROVED
                .replace(" upload='never'", "")
                .replace("    <tag k='note:stop_id' v='L7-POLANCO-N-01' />"
                         "\r\n", "")
                .replace("<tag k='note:miro_id' v='3458' />", "")
                .replace("    <tag k='note:pathway_id' "
                         "v='L7-POLANCO-P-07' />\r\n", ""))
    assert pub.read_bytes() == expected.encode("utf-8")
    out = capsys.readouterr().out
    assert "etiquetas de traza quitadas: 3" in out
    assert "node: delete 1, modify 1, nuevo 1" in out

    # Fuera de la cadena de versiones y sin sobrescribir.
    assert latest_version_path(tmp_path, "polanco") == src
    assert next_version_path(tmp_path, "polanco").name == (
        "polanco-07-claude.osm")
    with pytest.raises(CommandError, match="no se sobrescribe"):
        call_command("publish_station_osm", str(src))
    with pytest.raises(CommandError, match="ya es una copia"):
        call_command("publish_station_osm", str(pub),
                     out_dir=str(tmp_path / "otra"))

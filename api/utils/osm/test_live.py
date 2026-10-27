"""Contraste con OSM vivo, con la API simulada."""
from .live import API, check, read_file

OSM = """<?xml version='1.0' encoding='UTF-8'?>
<osm version='0.6'>
  <node id='10' action='modify' version='3' lat='19.4' lon='-99.1'/>
  <node id='11' action='modify' version='5' lat='19.4' lon='-99.1'/>
  <node id='12' action='delete' version='2' lat='19.4' lon='-99.1'/>
  <node id='13' action='delete' version='1' lat='19.4' lon='-99.1'/>
  <node id='14' version='7' lat='19.4' lon='-99.1'/>
  <node id='-1' lat='19.4' lon='-99.1'/>
  <way id='20' action='modify' version='4'>
    <nd ref='10'/><nd ref='-1'/><nd ref='11'/>
  </way>
</osm>
"""

SERVER = {
    f"{API}/nodes.json?nodes=10,11,12,13": {"elements": [
        {"id": 10, "version": 3}, {"id": 11, "version": 6},
        {"id": 12, "version": 2}, {"id": 13, "version": 1}]},
    f"{API}/ways.json?ways=20": {"elements": [{"id": 20, "version": 4}]},
    # 12 sale del way 20, que viaja en el archivo sin él: no bloquea.
    f"{API}/node/12/ways.json": {"elements": [{"id": 20}]},
    # 13 sigue en un way que no viaja en el archivo.
    f"{API}/node/13/ways.json": {"elements": [{"id": 99}]},
    f"{API}/way/20/relations.json": {"elements": [{"id": 500}]},
}


def _get(calls):
    def get(url):
        calls.append(url)
        return SERVER.get(url, {"elements": []})
    return get


def test_live_check_reports_conflicts_blocks_and_missing_relations(
        tmp_path):
    path = tmp_path / "estacion-01-claude.osm"
    path.write_text(OSM)
    calls = []
    report = check(read_file(path), _get(calls))
    assert report.checked == 5
    assert report.conflicts == [
        "node 11: el archivo trae v5, OSM está en v6"]
    assert report.gone == []
    assert report.blocked == [
        "node 13 sale de baja pero el way 99 de OSM lo sigue usando"]
    assert report.missing_relations == [
        "way 20 (modify) es miembro de la relación 500, que no viaja en "
        "el archivo"]
    assert report.failed
    assert not any("14" in u for u in calls), "sin action no se consulta"


def test_batch_with_a_missing_id_falls_back_to_single_fetches(tmp_path):
    path = tmp_path / "estacion-01-claude.osm"
    path.write_text("<osm version='0.6'>"
                    "<node id='10' action='modify' version='3' lat='0' "
                    "lon='0'/><node id='11' action='modify' version='1' "
                    "lat='0' lon='0'/></osm>")
    answers = {f"{API}/nodes.json?nodes=10,11": None,
               f"{API}/node/10.json": {"elements": [
                   {"id": 10, "version": 3}]},
               f"{API}/node/11.json": None}
    report = check(read_file(path),
                   lambda url: answers.get(url, {"elements": []}))
    assert report.conflicts == []
    assert report.gone == ["node 11: no existe o ya está borrado en OSM"]
    assert report.failed

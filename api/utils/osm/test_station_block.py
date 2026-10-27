"""Piezas del bloque por estación que no necesitan la base."""
from pathlib import Path

from . import tags as T
from .template import FamilyTemplate

TEMPLATE = (Path(__file__).resolve().parents[3] / "data" / "osm"
            / "templates" / "l7-deep-cascade.json")


def test_osm_tags_se_separa_del_bloque():
    # `osm_tags` no es una pieza de la plantilla: si llegara al parche,
    # el bloque fallaría por traer una sección que no se aplica.
    template = FamilyTemplate.load(TEMPLATE, "0200L7-CONSTITUYENTES")
    assert template.osm_tags["way/1368217717"]["building"] == "roof"
    assert FamilyTemplate.load(TEMPLATE, "0200L7-SANPEDROPINOS").osm_tags == {}


def test_keys_cambia_de_papel_el_tercer_banco():
    template = FamilyTemplate.load(TEMPLATE, "0200L7-CONSTITUYENTES")
    assert (template.banks["cascada-oriente-3"]["from"],
            template.banks["cascada-oriente-3"]["to"]) == ("N-09", "N-03")
    assert (template.banks["cascada-poniente-3"]["from"],
            template.banks["cascada-poniente-3"]["to"]) == ("N-08", "N-07")


def test_connector_que_cambia_de_nivel_es_escalera_exterior():
    tags = T.connector_steps_tags(-1, 0, "up")
    assert tags == {"highway": "steps", "level": "-1;0", "incline": "up",
                    "wheelchair": "no"}
    assert "indoor" not in tags


def test_pie_de_escalera_exterior_llega_al_nodo_tras_el_parche_local():
    # `connector_foot` va en `local` (marco de la estación) y el builder
    # lo lee del nodo ya parchado: tiene que sobrevivir a la mezcla.
    template = FamilyTemplate.load(TEMPLATE, "0200L7-CONSTITUYENTES")
    data = template.apply_local_patch(template.data)
    assert data["nodes"]["E-01"]["connector_foot"] == [13.6968, -21.2943]
    assert data["nodes"]["E-01"]["connector_level"] == 0


def test_connector_foot_parte_en_andador_y_escalera_exterior():
    # Constituyentes poniente: la entrada está en la plaza hundida (-1) y
    # la peatonal en la banqueta (0); el pie de la escalera exterior es
    # un punto fijo, y del acceso a él se camina en el -1.
    from .builder import split_connector_at_foot
    from .document import OsmDocument
    from .geometry import LocalFrame

    doc = OsmDocument(LocalFrame(19.4, -99.1, 0.0))
    entrance = doc.node_at(17.76, -35.94)
    tip = doc.node_at(21.47, -21.43)
    # Un nodo interior a 0.1 m del pie: el pie no debe soldarse a él.
    inner = doc.node_at(13.75, -21.30)
    steps_tags = T.connector_steps_tags(-1, 0, "up")
    walk, steps = split_connector_at_foot(
        doc, entrance, tip, (13.6968, -21.2943), -1, 0, steps_tags)
    foot = walk.nodes[-1]
    assert walk.nodes == [entrance, foot] and steps.nodes == [foot, tip]
    assert foot != inner and foot in doc.outdoor
    assert walk.tags == {"highway": "footway", "level": "-1"}
    assert steps.tags == {"highway": "steps", "level": "-1;0",
                          "incline": "up", "wheelchair": "no"}
    assert walk.levels == (-1,) and steps.levels == (-1, 0)

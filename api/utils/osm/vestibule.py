"""Vestíbulo longitudinal de nivel 1 sobre un andén central (Tlalpan).

En la superficie de la Calzada de Tlalpan el vestíbulo no es una losa
transversal sino una pasarela a lo largo del andén, con los torniquetes
encima, a la que llegan las escaleras del andén en serie y los dos brazos
del puente. El grafo lo modela como un solo nodo; esta sección de la
plantilla dice cómo se reparte y el generador la convierte en aristas y
`extra_ways` antes de dibujar, ya con los brazos del área resueltos.

Todas las u se miden desde `centre` (el centro del vestíbulo), salvo la
del nodo de encuentro, `meeting`. Las dos suelen coincidir; se declaran
aparte porque son decisiones distintas: dónde se juntan los brazos y
dónde cuelga lo demás.
"""
from __future__ import annotations

import copy
import math

from .template import TemplateError, edge_key

# Lo que se acerca un brazo al nodo de encuentro en u sin hacer el tramo
# transversal: por debajo baja derecho, como el poniente de Portales.
STRAIGHT_ARM_M = 0.25


def _edges_by_key(data: dict) -> dict:
    return {edge_key(e): e for e in data.get("edges", [])}


def _stair_runs(spec: dict, centre: float, rise: float, limits) -> dict:
    """{arista: (u del pie, u de la llegada, largo)} de las del andén.

    La llegada queda fija sobre la pasarela; el largo es `length` o el
    máximo que deje `clear` metros en u hasta la llegada de la siguiente
    escalera hacia afuera, y el pie se corre a lo largo del andén.
    """
    landings = {k: float(d) for k, d in spec["landings"].items()}
    length = float(spec.get("length", 12.5))
    clear = float(spec.get("clear", 1.5))
    out = {}
    for key, d in landings.items():
        sign = 1.0 if d >= 0 else -1.0
        outward = [abs(o) for o in landings.values()
                   if o * sign > 0 and abs(o) > abs(d)]
        run = math.sqrt(max(length ** 2 - rise ** 2, 0.0))
        if outward:
            run = min(run, min(outward) - abs(d) - clear)
        land_u = centre + d
        end = limits[1] if sign > 0 else limits[0]
        room = abs(end - land_u) - clear
        run = min(run, room)
        if run <= 0:
            raise TemplateError(
                f"la escalera del andén {key} no cabe: su llegada en "
                f"u={land_u:.2f} no deja {clear:g} m libres hacia afuera")
        out[key] = (land_u + sign * run, land_u, math.hypot(run, rise))
    return out


def expand_vestibule(data: dict) -> tuple[dict, list[str]]:
    """Copia de la plantilla con el vestíbulo convertido en piezas.

    Devuelve también las líneas de reporte. Sin sección `vestibule` la
    plantilla queda intacta.
    """
    spec = data.get("vestibule")
    if not spec:
        return data, []
    out = copy.deepcopy(data)
    out.pop("vestibule")
    platform = spec["platform"]
    node = spec["node"]
    centre = float(spec["centre"])
    meeting = float(spec["meeting"])
    walk = spec["walkway"]
    dv = float(walk["dv"])
    reach = [float(r) for r in walk["reach"]]
    north, south = centre + max(reach), centre + min(reach)
    gates = sorted(centre + float(t) for t in spec.get("turnstiles", []))
    if gates and not (gates[0] < meeting < gates[-1]):
        raise TemplateError(
            f"el nodo de encuentro del vestíbulo (u={meeting:.2f}) queda "
            f"fuera de los torniquetes ({gates[0]:.2f} a {gates[-1]:.2f}): "
            f"una escalera del andén se alcanzaría sin pasar por ellos")
    if not south < meeting < north:
        raise TemplateError(
            f"el nodo de encuentro del vestíbulo (u={meeting:.2f}) queda "
            f"fuera de la pasarela ({south:.2f} a {north:.2f})")
    # Un solo way de punta a punta, con el nodo de encuentro de vértice y
    # los dos torniquetes medidos desde la punta sur: así lo dejaron
    # Portales 05 y General Anaya 06.
    piece = {"id": walk["id"], "level": walk.get("level", 1),
             "tags": dict(walk.get("tags", {})),
             "geometry": [{"spine": platform, "u": south, "dv": dv},
                          {"spine": platform, "u": meeting, "dv": dv},
                          {"spine": platform, "u": north, "dv": dv}],
             "comment": walk.get("comment", "")}
    if gates:
        piece["turnstile"] = [{"from": [south, 0.0], "distance": g - south}
                              for g in gates]
    out.setdefault("extra_ways", []).append(piece)
    nodes = out.setdefault("nodes", {})
    if node in nodes:
        nodes[node] = dict(nodes[node], u=meeting)
    edges = _edges_by_key(out)
    report = [f"vestíbulo: centro en u={centre:.2f}, nodo de encuentro en "
              f"u={meeting:.2f}, pasarela de u {south:.2f} a {north:.2f} "
              f"a dv {dv:+.2f} de la senda"
              + (", torniquetes en u " + " y ".join(f"{g:.2f}"
                                                    for g in gates)
                 if gates else "")]
    stairs = spec.get("stairs")
    if stairs:
        p_spec = out["nodes"][platform]
        half = float(p_spec["length"]) / 2
        limits = (float(p_spec["u"]) - half, float(p_spec["u"]) + half)
        runs = _stair_runs(stairs, centre, dv, limits)
        for key, (foot, land, length) in sorted(runs.items()):
            if key not in edges:
                raise TemplateError(
                    f"el vestíbulo dibuja la escalera del andén {key}, "
                    f"que la plantilla no declara en edges")
            edges[key]["geometry"] = [
                {"spine": platform, "u": round(foot, 3)},
                {"spine": platform, "u": round(land, 3), "dv": dv}]
            report.append(f"vestíbulo: escalera del andén {key}, pie en "
                          f"u={foot:.2f}, llegada en u={land:.2f}, "
                          f"{length:.2f} m")
    for key, arm in sorted(spec.get("arms", {}).items()):
        if key == "comment":
            continue
        if key not in edges:
            raise TemplateError(
                f"el vestíbulo dibuja el brazo {key}, que la plantilla no "
                f"declara en edges")
        axis = float(arm["axis"])
        geometry = [edges[key]["from"]]
        # La cabecera de un banco que sube a lo largo de un lóbulo ancho
        # queda en el borde del brazo, no en su eje: el pasillo llega al
        # eje en transversal antes de bajar por él (Portales 05).
        head = nodes.get(edges[key]["from"], {})
        head_u, head_v = head.get("u"), head.get("v")
        if (isinstance(head_u, (int, float))
                and isinstance(head_v, (int, float))
                and abs(float(head_u) - axis) > STRAIGHT_ARM_M):
            geometry.append([axis, float(head_v)])
        if abs(axis - meeting) > STRAIGHT_ARM_M:
            cross = dv + float(arm["cross"])
            geometry += [{"spine": platform, "u": axis, "dv": cross},
                         {"spine": platform, "u": meeting, "dv": cross}]
        geometry.append({"spine": platform, "u": meeting, "dv": dv})
        edges[key]["geometry"] = geometry
        edges[key].pop("turnstile", None)
    return out, report

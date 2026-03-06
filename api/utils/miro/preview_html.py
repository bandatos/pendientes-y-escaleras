"""Utilities to convert MiroSchemaBuilder output to a Cytoscape.js HTML."""
import json

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NODE_SHAPE: dict[int | None, str] = {
    0: "round-rectangle",  # Platform
    2: "rectangle",        # Entrance/Exit
    3: "ellipse",          # Generic node
}

EDGE_COLOR: dict[int, str] = {
    1: "#888888",  # Walkway
    2: "#444444",  # Stairs
    3: "#067429",  # Moving sidewalk
    4: "#6631d7",  # Escalator
    5: "#305bab",  # Elevator
}

EDGE_LABEL: dict[int, str] = {
    1: "Pasillo",
    2: "Escaleras",
    3: "Movedizo",
    4: "Escalera mecánica",
    5: "Ascensor",
}

_X_SPACING   = 220   # px between nodes on same level
_Y_SPACING   = 280   # px between levels
_X_OFFSET    = 100   # left margin
_Y_OFFSET    = 80    # top margin
_X_GROUP_GAP = 80    # extra px between route groups on the same level

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_cytoscape_elements(result: dict) -> list[dict]:
    """Convert MiroSchemaBuilder.run() output to Cytoscape.js elements.

    Args:
        result: Dict with keys 'levels', 'stops', 'pathways', 'skipped'.
            Stops are serialized by StopCatSerializer (uses ``route_line``
            and ``location_type`` fields). Pathways by PathwaySerializer.

    Returns:
        List of Cytoscape element dicts (nodes and edges).
    """
    elements: list[dict] = []

    levels: list[dict] = result.get("levels", [])
    stops: list[dict] = result.get("stops", [])
    pathways: list[dict] = result.get("pathways", [])

    # Map level_index -> Y position.
    # Invert: higher level_index = higher on screen (smaller Y).
    level_indices = sorted(
        {lv["level_index"] for lv in levels}, reverse=True
    )
    index_to_y: dict[float, float] = {
        idx: _Y_OFFSET + i * _Y_SPACING
        for i, idx in enumerate(level_indices)
    }

    # Group stops by (route_line, level_index) for independent X placement.
    stops_by_route_level: dict[tuple, list[dict]] = {}
    for stop in stops:
        key = (stop.get("route_line") or "", stop.get("level_index"))
        stops_by_route_level.setdefault(key, []).append(stop)

    # For each level_index, compute the starting X of each route group.
    # Route groups are sorted alphabetically within the same level.
    level_route_start_x: dict[float | None, dict[str, float]] = {}
    for level_idx in {k[1] for k in stops_by_route_level}:
        routes_at_level = sorted(
            route
            for (route, idx) in stops_by_route_level
            if idx == level_idx
        )
        cur_x = _X_OFFSET
        route_start: dict[str, float] = {}
        for route in routes_at_level:
            route_start[route] = cur_x
            n = len(stops_by_route_level[(route, level_idx)])
            cur_x += n * _X_SPACING + _X_GROUP_GAP
        level_route_start_x[level_idx] = route_start

    # Build stop nodes.
    stop_id_set = {s["stop_id"] for s in stops}
    for (route_line, level_key), level_stops in stops_by_route_level.items():
        y = index_to_y.get(
            level_key, _Y_OFFSET + len(index_to_y) * _Y_SPACING
        )
        start_x = level_route_start_x.get(
            level_key, {}
        ).get(route_line, _X_OFFSET)
        for i, stop in enumerate(level_stops):
            x = start_x + i * _X_SPACING
            loc_type = stop.get("location_type")
            shape = NODE_SHAPE.get(loc_type, "ellipse")
            is_closed = stop.get("is_closed", False)
            label = stop.get("stop_name", "")
            if stop.get("stop_desc"):
                label += f"\n({stop['stop_desc']})"
            if route_line:
                label = f"[{route_line}] {label}"

            elements.append({
                "data": {
                    "id": stop["stop_id"],
                    "label": label,
                    "stop_id": stop["stop_id"],
                    "stop_name": stop.get("stop_name", ""),
                    "miro_id": stop.get("miro_id", ""),
                    "location_type": loc_type,
                    "route": route_line,
                    "level_index": level_key,
                    "stop_code": stop.get("stop_code", ""),
                    "shape": shape,
                    "closed": is_closed,
                },
                "position": {"x": x, "y": y},
            })

    # Build level label nodes — one per (route, level_index) pair.
    for level in levels:
        idx = level["level_index"]
        y = index_to_y.get(idx, _Y_OFFSET)
        level_id = level.get("level_id", f"level-{idx}")
        level_name = level.get("level_name") or ""
        route_line = level.get("route_line") or ""
        label = f"{route_line} Nivel {idx}"
        if level_name:
            label += f" — {level_name}"
        start_x = level_route_start_x.get(
            idx, {}).get(route_line, _X_OFFSET)
        elements.append({
            "data": {
                "id": f"__level__{level_id}",
                "label": label,
                "is_level_node": True,
            },
            "position": {"x": start_x - 140, "y": y},
        })

    # Build pathway edges — from_stop/to_stop are real stop_ids.
    stop_id_set = {s["stop_id"] for s in stops}
    for pw in pathways:
        from_id = pw.get("from_stop", "")
        to_id = pw.get("to_stop", "")
        if from_id not in stop_id_set or to_id not in stop_id_set:
            continue
        mode = pw.get("pathway_mode", 1)
        bidir = pw.get("is_bidirectional", 0)
        color = EDGE_COLOR.get(mode, "#aaaaaa")
        desc = pw.get("pathway_description") or ""
        edge_label = EDGE_LABEL.get(mode, f"Modo {mode}")
        elements.append({
            "data": {
                "id": pw.get("pathway_id", f"{from_id}-{to_id}"),
                "source": from_id,
                "target": to_id,
                "pathway_mode": mode,
                "mode_label": edge_label,
                "is_bidirectional": bidir,
                "description": desc,
                "color": color,
                "miro_id": pw.get("miro_id", ""),
            },
        })

    return elements


def render_html(
    elements: list[dict],
    title: str,
    skipped: list[dict] | None = None,
) -> str:
    """Render a standalone HTML page with a Cytoscape.js graph.

    Args:
        elements: Cytoscape element dicts from build_cytoscape_elements().
        title: Page/graph title (frame name).
        skipped: Optional list of skipped items from MiroSchemaBuilder.

    Returns:
        Full HTML string.
    """
    elements_json = json.dumps(elements, ensure_ascii=False, indent=2)
    skipped_rows = ""
    for item in (skipped or []):
        miro_id = item.get("miro_id", "—")
        reason = item.get("reason", "—")
        skipped_rows += (
            f"<tr><td>{miro_id}</td><td>{reason}</td></tr>\n"
        )

    legend_items = ""
    for mode_id, color in EDGE_COLOR.items():
        label = EDGE_LABEL.get(mode_id, f"Modo {mode_id}")
        legend_items += (
            f'<li><span class="swatch" style="background:{color}"></span>'
            f'{label}</li>\n'
        )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <title>Preview: {title}</title>
  <script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js">
  </script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: sans-serif; display: flex;
            flex-direction: column; height: 100vh; overflow: hidden; }}
    h1 {{ padding: 8px 16px; font-size: 1rem; background: #1e1e2e;
          color: #cdd6f4; flex-shrink: 0; }}
    #main {{ display: flex; flex: 1; overflow: hidden; }}
    #cy {{ flex: 1; background: #f8f8f8; }}
    #sidebar {{ width: 260px; overflow-y: auto; padding: 12px;
                border-left: 1px solid #ccc; font-size: 0.8rem;
                background: #fff; }}
    #sidebar h2 {{ font-size: 0.85rem; margin-bottom: 8px;
                   color: #555; border-bottom: 1px solid #eee;
                   padding-bottom: 4px; }}
    #tooltip {{ margin-bottom: 16px; }}
    #tooltip p {{ margin: 2px 0; word-break: break-all; }}
    #tooltip strong {{ display: inline-block; min-width: 80px;
                       color: #333; }}
    legend-section ul {{ list-style: none; }}
    .swatch {{ display: inline-block; width: 14px; height: 14px;
               border-radius: 2px; margin-right: 6px;
               vertical-align: middle; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.75rem; }}
    th, td {{ border: 1px solid #ddd; padding: 3px 5px;
              text-align: left; vertical-align: top; }}
    th {{ background: #f0f0f0; }}
    #skipped-section {{ margin-top: 16px; }}
  </style>
</head>
<body>
  <h1>Miro Preview &mdash; {title}</h1>
  <div id="main">
    <div id="cy"></div>
    <div id="sidebar">
      <h2>Selecciona un nodo o arista</h2>
      <div id="tooltip"><p style="color:#999">Haz click en un elemento</p>
      </div>
      <div class="legend-section">
        <h2>Leyenda — Pathways</h2>
        <ul>{legend_items}</ul>
      </div>
      <div class="legend-section" style="margin-top:12px">
        <h2>Leyenda — Nodos</h2>
        <ul>
          <li>Rect = Entrada/Salida (type 2)</li>
          <li>Rect redondeado = Plataforma (type 0)</li>
          <li>Elipse = Nodo genérico (type 3)</li>
          <li style="color:red">Borde rojo = CLAUSURADO</li>
        </ul>
      </div>
      <div id="skipped-section">
        <h2>Skipped ({len(skipped or [])})</h2>
        <table>
          <tr><th>miro_id</th><th>reason</th></tr>
          {skipped_rows or '<tr><td colspan="2">Ninguno</td></tr>'}
        </table>
      </div>
    </div>
  </div>
  <script>
    const elements = {elements_json};

    const cy = cytoscape({{
      container: document.getElementById('cy'),
      elements: elements,
      style: [
        {{
          selector: 'node[!is_level_node]',
          style: {{
            'shape': 'data(shape)',
            'label': 'data(label)',
            'text-wrap': 'wrap',
            'text-max-width': '160px',
            'font-size': '10px',
            'width': '160px',
            'height': '55px',
            'background-color': '#b0c4de',
            'border-width': 2,
            'border-color': '#5577aa',
            'text-valign': 'center',
            'text-halign': 'center',
            'padding': '6px',
          }}
        }},
        {{
          selector: 'node[?closed]',
          style: {{
            'border-color': 'red',
            'border-style': 'dashed',
            'border-width': 3,
          }}
        }},
        {{
          selector: 'node[is_level_node]',
          style: {{
            'shape': 'rectangle',
            'label': 'data(label)',
            'font-size': '11px',
            'font-weight': 'bold',
            'color': '#666',
            'background-color': '#e8e8e8',
            'background-opacity': 0.5,
            'border-width': 1,
            'border-color': '#bbb',
            'width': '180px',
            'height': '40px',
            'text-valign': 'center',
            'text-halign': 'center',
          }}
        }},
        {{
          selector: 'edge',
          style: {{
            'width': 2.5,
            'line-color': 'data(color)',
            'target-arrow-color': 'data(color)',
            'target-arrow-shape': 'triangle',
            'source-arrow-shape': function(ele) {{
              return ele.data('is_bidirectional') ? 'triangle' : 'none';
            }},
            'source-arrow-color': 'data(color)',
            'curve-style': 'bezier',
            'label': 'data(mode_label)',
            'font-size': '9px',
            'text-rotation': 'autorotate',
            'color': '#555',
          }}
        }},
        {{
          selector: 'node:selected, edge:selected',
          style: {{
            'border-color': '#ff9900',
            'border-width': 3,
            'line-color': '#ff9900',
          }}
        }},
      ],
      layout: {{
        name: 'preset',
      }},
      userZoomingEnabled: true,
      userPanningEnabled: true,
      boxSelectionEnabled: false,
    }});

    cy.fit(cy.nodes('[!is_level_node]'), 60);

    const tooltip = document.getElementById('tooltip');
    const sidebar = document.getElementById('sidebar').querySelector('h2');

    cy.on('tap', 'node[!is_level_node]', function(evt) {{
      const d = evt.target.data();
      sidebar.textContent = 'Nodo seleccionado';
      tooltip.innerHTML = `
        <p><strong>stop_id:</strong> ${{d.stop_id}}</p>
        <p><strong>stop_name:</strong> ${{d.stop_name}}</p>
        <p><strong>miro_id:</strong> ${{d.miro_id}}</p>
        <p><strong>loc_type:</strong> ${{d.location_type}}</p>
        <p><strong>route:</strong> ${{d.route}}</p>
        <p><strong>nivel:</strong> ${{d.level_index}}</p>
        <p><strong>stop_code:</strong> ${{d.stop_code || '—'}}</p>
        <p><strong>closed:</strong> ${{d.closed ? '⚠️ SÍ' : 'No'}}</p>
      `;
    }});

    cy.on('tap', 'edge', function(evt) {{
      const d = evt.target.data();
      sidebar.textContent = 'Arista seleccionada';
      tooltip.innerHTML = `
        <p><strong>pathway_id:</strong> ${{d.id}}</p>
        <p><strong>from:</strong> ${{d.source}}</p>
        <p><strong>to:</strong> ${{d.target}}</p>
        <p><strong>modo:</strong> ${{d.mode_label}} (${{d.pathway_mode}})</p>
        <p><strong>bidireccional:</strong> ${{d.is_bidirectional ? 'Sí' : 'No'}}</p>
        <p><strong>desc:</strong> ${{d.description || '—'}}</p>
        <p><strong>miro_id:</strong> ${{d.miro_id}}</p>
      `;
    }});

    cy.on('tap', function(evt) {{
      if (evt.target === cy) {{
        sidebar.textContent = 'Selecciona un nodo o arista';
        tooltip.innerHTML =
          '<p style="color:#999">Haz click en un elemento</p>';
      }}
    }});
  </script>
</body>
</html>"""
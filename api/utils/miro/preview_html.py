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

# Background color per location_type
NODE_COLOR: dict[int | None, str] = {
    0: "#aec6e8",   # Platform  — blue
    2: "#b8e0b8",   # Entrance  — green
    3: "#d4c5e8",   # Generic   — purple
}

NODE_BORDER: dict[int | None, str] = {
    0: "#4a86c8",
    2: "#4a9a4a",
    3: "#7a5ab8",
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

# Grid-layout fallback constants (used when miro_positions is unavailable)
_X_SPACING   = 220
_Y_SPACING   = 280
_X_OFFSET    = 100
_Y_OFFSET    = 80
_X_GROUP_GAP = 80
_DEFAULT_W   = 160
_DEFAULT_H   = 55
# Gap to the left of the leftmost stop for level labels (Miro mode)
_LABEL_MARGIN = 180

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_cytoscape_elements(result: dict) -> list[dict]:
    """Convert MiroSchemaBuilder.run() output to Cytoscape.js elements.

    When ``miro_positions`` is present in *result* (direct Miro import),
    nodes are placed at their actual Miro coordinates so the preview
    mirrors the Miro diagram. Falls back to a computed grid layout when
    the result comes from the DB (``--from-db`` mode).

    Args:
        result: Dict with keys 'levels', 'stops', 'pathways', 'skipped',
            and optionally 'miro_positions' and 'frame_size'.

    Returns:
        List of Cytoscape element dicts (nodes and edges).
    """
    elements: list[dict] = []
    levels: list[dict] = result.get("levels", [])
    stops: list[dict] = result.get("stops", [])
    pathways: list[dict] = result.get("pathways", [])
    miro_pos: dict = result.get("miro_positions") or {}
    frame_size: dict = result.get("frame_size") or {}
    use_miro = bool(miro_pos)
    stop_id_set = {s["stop_id"] for s in stops}

    # --- Compute node positions and sizes -----------------------------------
    # stop_xy: stop_id -> (x, y) in Cytoscape model units
    # stop_wh: stop_id -> (width, height) in Cytoscape model units
    # level_label_xy: level_id -> (x, y)
    stop_xy: dict[str, tuple[float, float]] = {}
    stop_wh: dict[str, tuple[float, float]] = {}
    level_label_xy: dict[str, tuple[float, float]] = {}

    if use_miro:
        # Miro items use relativeTo="parent_top_left", origin="center":
        # position.x/y is the center of the item relative to the frame
        # top-left corner, which maps 1:1 to Cytoscape model coordinates.
        for stop in stops:
            sid = stop["stop_id"]
            mid = stop.get("miro_id", "")
            if mid and mid in miro_pos:
                mp = miro_pos[mid]
                stop_xy[sid] = (mp["x"], mp["y"])
                stop_wh[sid] = (mp["width"], mp["height"])
            else:
                stop_xy[sid] = (0.0, 0.0)
                stop_wh[sid] = (_DEFAULT_W, _DEFAULT_H)

        for level in levels:
            idx = level.get("level_index")
            level_id = level.get("level_id", f"level-{idx}")
            route_line = level.get("route_line") or ""
            lvl_pts = [
                stop_xy[s["stop_id"]] for s in stops
                if s.get("level_index") == idx
                and (s.get("route_line") or "") == route_line
                and s["stop_id"] in stop_xy
            ]
            if lvl_pts:
                avg_y = sum(p[1] for p in lvl_pts) / len(lvl_pts)
                min_x = min(p[0] for p in lvl_pts)
                level_label_xy[level_id] = (
                    min_x - _LABEL_MARGIN, avg_y)
            else:
                level_label_xy[level_id] = (
                    -_LABEL_MARGIN, (idx or 0) * _Y_SPACING)
    else:
        # Grid layout: one row per level (highest level_index at top),
        # stops grouped by route within each row.
        level_indices = sorted(
            {lv["level_index"] for lv in levels}, reverse=True
        )
        index_to_y: dict = {
            idx: _Y_OFFSET + i * _Y_SPACING
            for i, idx in enumerate(level_indices)
        }
        stops_by_rl: dict = {}
        for stop in stops:
            key = (stop.get("route_line") or "", stop.get("level_index"))
            stops_by_rl.setdefault(key, []).append(stop)

        rl_start_x: dict = {}
        for level_idx in {k[1] for k in stops_by_rl}:
            routes = sorted(
                r for (r, i) in stops_by_rl if i == level_idx)
            cur_x = _X_OFFSET
            rx: dict = {}
            for route in routes:
                rx[route] = cur_x
                n = len(stops_by_rl[(route, level_idx)])
                cur_x += n * _X_SPACING + _X_GROUP_GAP
            rl_start_x[level_idx] = rx

        for (rl, lvl_key), lvl_stops in stops_by_rl.items():
            y = index_to_y.get(
                lvl_key, _Y_OFFSET + len(index_to_y) * _Y_SPACING)
            sx = rl_start_x.get(lvl_key, {}).get(rl, _X_OFFSET)
            for i, stop in enumerate(lvl_stops):
                sid = stop["stop_id"]
                stop_xy[sid] = (sx + i * _X_SPACING, y)
                stop_wh[sid] = (_DEFAULT_W, _DEFAULT_H)

        for level in levels:
            idx = level.get("level_index")
            level_id = level.get("level_id", f"level-{idx}")
            route_line = level.get("route_line") or ""
            y = index_to_y.get(idx, _Y_OFFSET)
            sx = rl_start_x.get(idx, {}).get(route_line, _X_OFFSET)
            level_label_xy[level_id] = (sx - 140, y)

    # --- Frame background (Miro mode only) ----------------------------------
    if use_miro and frame_size:
        fw = frame_size.get("width", 1000)
        fh = frame_size.get("height", 800)
        elements.append({
            "data": {
                "id": "__frame__",
                "is_frame_node": True,
                "node_width": fw,
                "node_height": fh,
            },
            "position": {"x": fw / 2, "y": fh / 2},
        })

    # --- Level label nodes --------------------------------------------------
    for level in levels:
        idx = level.get("level_index")
        level_id = level.get("level_id", f"level-{idx}")
        level_name = level.get("level_name") or ""
        route_line = level.get("route_line") or ""
        label = f"{route_line} Nivel {idx}"
        if level_name:
            label += f" — {level_name}"
        lx, ly = level_label_xy.get(level_id, (0.0, 0.0))
        elements.append({
            "data": {
                "id": f"__level__{level_id}",
                "label": label,
                "is_level_node": True,
            },
            "position": {"x": lx, "y": ly},
        })

    # --- Stop nodes ---------------------------------------------------------
    for stop in stops:
        sid = stop["stop_id"]
        loc_type = stop.get("location_type")
        x, y = stop_xy.get(sid, (0.0, 0.0))
        w, h = stop_wh.get(sid, (_DEFAULT_W, _DEFAULT_H))
        shape = NODE_SHAPE.get(loc_type, "ellipse")
        color = NODE_COLOR.get(loc_type, "#b0c4de")
        border_c = NODE_BORDER.get(loc_type, "#5577aa")
        is_closed = stop.get("is_closed", False)
        route_line = stop.get("route_line") or ""
        label = stop.get("stop_name", "")
        if stop.get("stop_desc"):
            label += f"\n({stop['stop_desc']})"
        if route_line:
            label = f"[{route_line}] {label}"
        elements.append({
            "data": {
                "id": sid,
                "label": label,
                "stop_id": sid,
                "stop_name": stop.get("stop_name", ""),
                "miro_id": stop.get("miro_id", ""),
                "location_type": loc_type,
                "route": route_line,
                "level_index": stop.get("level_index"),
                "stop_code": stop.get("stop_code", ""),
                "shape": shape,
                "closed": is_closed,
                "node_width": w,
                "node_height": h,
                "bg_color": color,
                "border_color": border_c,
            },
            "position": {"x": x, "y": y},
        })

    # --- Pathway edges ------------------------------------------------------
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

    node_legend = ""
    loc_labels = {
        0: ("Plataforma/andén (type 0)", NODE_COLOR[0]),
        2: ("Entrada/Salida (type 2)", NODE_COLOR[2]),
        3: ("Nodo genérico (type 3)", NODE_COLOR[3]),
    }
    for _, (lbl, col) in loc_labels.items():
        node_legend += (
            f'<li><span class="swatch" style="background:{col}"></span>'
            f'{lbl}</li>\n'
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
    #cy {{ flex: 1; background: #f0f0f0; }}
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
    .legend-section ul {{ list-style: none; }}
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
      <div id="tooltip">
        <p style="color:#999">Haz click en un elemento</p>
      </div>
      <div class="legend-section">
        <h2>Leyenda — Pathways</h2>
        <ul>{legend_items}</ul>
      </div>
      <div class="legend-section" style="margin-top:12px">
        <h2>Leyenda — Nodos</h2>
        <ul>
          {node_legend}
          <li style="color:red">Borde rojo punteado = CLAUSURADO</li>
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
        // Frame background — rendered first (behind everything else)
        {{
          selector: 'node[?is_frame_node]',
          style: {{
            'shape': 'rectangle',
            'width': 'data(node_width)',
            'height': 'data(node_height)',
            'background-color': '#ffffff',
            'background-opacity': 0.6,
            'border-width': 1,
            'border-color': '#bbbbbb',
            'border-style': 'dashed',
            'label': '',
            'events': 'no',
            'z-index': 0,
          }}
        }},
        // Stop nodes
        {{
          selector: 'node[!is_level_node][!is_frame_node]',
          style: {{
            'shape': 'data(shape)',
            'label': 'data(label)',
            'text-wrap': 'wrap',
            'text-max-width': '120px',
            'font-size': '10px',
            'width': 'data(node_width)',
            'height': 'data(node_height)',
            'background-color': 'data(bg_color)',
            'border-width': 2,
            'border-color': 'data(border_color)',
            'text-valign': 'center',
            'text-halign': 'center',
            'padding': '6px',
            'z-index': 2,
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
        // Level label nodes
        {{
          selector: 'node[?is_level_node]',
          style: {{
            'shape': 'rectangle',
            'label': 'data(label)',
            'font-size': '11px',
            'font-weight': 'bold',
            'color': '#444',
            'background-color': '#e8e8e8',
            'background-opacity': 0.85,
            'border-width': 1,
            'border-color': '#aaa',
            'width': '180px',
            'height': '40px',
            'text-valign': 'center',
            'text-halign': 'center',
            'z-index': 1,
          }}
        }},
        // Edges
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
            'z-index': 3,
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
      layout: {{ name: 'preset' }},
      userZoomingEnabled: true,
      userPanningEnabled: true,
      boxSelectionEnabled: false,
    }});

    // Fit viewport to stop/level nodes, excluding the frame background
    cy.fit(cy.nodes('[!is_frame_node]'), 60);

    const tooltip = document.getElementById('tooltip');
    const sidebar = document.getElementById('sidebar').querySelector('h2');

    cy.on('tap', 'node[!is_level_node][!is_frame_node]', function(evt) {{
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
        <p><strong>bidireccional:</strong>
           ${{d.is_bidirectional ? 'Sí' : 'No'}}</p>
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

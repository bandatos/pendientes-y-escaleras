---
name: miro-api
description: Referencia de la API REST v2 de Miro usada en MiroSchemaBuilder.
  Usar cuando se trabaje con utils/miro/, se modifique builder.py, frames.py,
  o se necesite entender la estructura de ítems, frames, conectores y coordenadas de Miro.
user-invocable: false
---

# Miro REST API v2 — Referencia para MiroSchemaBuilder

## Acceso

```python
# utils/miro/helpers.py
base_url = f"https://api.miro.com/v2/boards/{MIRO_BOARD_ID}"
headers = {"Authorization": f"Bearer {MIRO_ACCESS_TOKEN}", "Accept": "application/json"}
```

Paginación: `get_all_paginated(url, params)` — itera por `cursor` hasta agotar resultados.

---

## Frames

```python
# GET /v2/boards/{board_id}/items?type=frame
{
  "id": "3458764661678874975",
  "type": "frame",
  "data": {"title": "Mixcoac"},
  "position": {"x": float, "y": float, "origin": "center"},
  "geometry": {"width": float, "height": float}
}
```

**Coordenadas del frame** (en el tablero, origen = centro del frame):
```
top    = position.y - geometry.height / 2
bottom = position.y + geometry.height / 2
left   = position.x - geometry.width / 2
right  = position.x + geometry.width / 2
```

---

## Ítems dentro de un frame

```python
# GET /v2/boards/{board_id}/items?parent_item_id={frame_id}
```

Los ítems hijos usan `relativeTo: "parent_top_left"` y `origin: "center"`.
Esto significa que `position.x/y` es el **centro del ítem relativo al top-left del frame**.

```
item.position.y = 0                      → top del frame
item.position.y = frame.geometry.height  → bottom del frame
```

### Estructura común

```python
{
  "id": str,
  "type": "shape" | "text" | "connector",
  "data": {
    "content": "<p>HTML content</p>",  # Solo shape y text
    "shape": str,                       # Solo shape (ver tabla abajo)
  },
  "position": {"x": float, "y": float, "origin": "center",
               "relativeTo": "parent_top_left"},
  "geometry": {"width": float, "height": float},
  "style": {...},
  "parent": {"id": frame_id}
}
```

Centro de un ítem: `_item_center(item)` → `(position.x, position.y)` (`parsers.py`).

### Shapes relevantes

| `data.shape`      | Uso en MiroSchemaBuilder      |
|-------------------|-------------------------------|
| `round_rectangle` | Plataforma/andén (loc_type=0) |
| `rectangle`       | Entrada (loc_type=2)          |
| `circle`          | Nodo genérico (loc_type=3)    |
| `right_arrow`     | Divisor de nivel              |

Filtrado por shape: `LevelMixin.get_items_by_shape(shape)` (`level_mixin.py`).

---

## Conectores

```python
# GET /v2/boards/{board_id}/connectors
{
  "id": str,
  "type": "connector",
  "startItem": {"id": str},
  "endItem": {"id": str},
  "style": {
    "strokeColor": str,   # color determina el modo de pathway
    "strokeStyle": "normal" | "dashed",
    "startStrokeCap": "arrow" | "oval" | "diamond" | "none",
    "endStrokeCap":  "arrow" | "oval" | "diamond" | "none",
  },
  "captions": [{"content": "<p>HTML</p>"}]
}
```

### Colores → PathwayMode (`PathwayMixin._get_pathway_mode`)

| `strokeColor`                        | Modo | Descripción          |
|--------------------------------------|------|----------------------|
| `#6631d7`                            | 4    | Escalera mecánica    |
| `#305bab`                            | 5    | Ascensor             |
| `#067429`                            | 3    | Banda transportadora |
| `#b0b0b0` + caps=`oval`/`oval`       | 1    | Pasillo (walkway)    |
| `#b0b0b0` (otros caps)               | 2    | Escaleras            |
| `strokeStyle=dashed` + caps=`diamond`| —    | Entrada doble (no pathway) |

### Bidireccionalidad (`PathwayMixin._get_bidirectional`)

| Modo           | Regla                                                         |
|----------------|---------------------------------------------------------------|
| 1 Pasillo      | Siempre bidireccional                                         |
| 5 Ascensor     | Siempre bidireccional                                         |
| 3 Movedizo     | Siempre unidireccional                                        |
| 4 Escalera     | **Documentado, no implementado**: la idea era «bidireccional si hay 2 conectores entre el mismo par de nodos»; `_build_escalator_pairs` se calcula pero `_get_bidirectional` lo ignora y aplica la regla de caps de Escaleras. Ricardo decide si se implementa o se elimina (`docs/tasks/task-24`, inciso a) |
| 2 Escaleras    | Bidireccional si ambos caps ≠ `none`; unidireccional si alguno es `none` |

### Descripción de connectores

`PathwayMixin._extract_description(connector)` extrae texto entre paréntesis de
`captions[].content` y los une con `"; "`.

### Entradas dobles (`StopMixin._find_double_pairs`)

Un conector `strokeStyle=dashed` con `startStrokeCap=diamond` y
`endStrokeCap=diamond` une dos entradas que representan la misma apertura física
(código A/B). `_get_double_stop_codes()` asigna `'A'` a la más a la izquierda
(menor X) y `'B'` a la derecha.

---

## Textos de nivel

Los ítems `type=text` dentro del frame marcan niveles. Formato esperado:

```
L7 Nivel superficie 0
L12 Nivel -1
L7 Nivel Andenes -3
Nivel -2          ← sin prefijo de línea → requiere unique_route
```

Regex `_LEVEL_TEXT_RE` en `parsers.py`:

```python
_LEVEL_TEXT_RE = re.compile(
    r'(?:(?P<line>L\d{1,2}[AB]?)\s+)?'
    r'NIVEL\s+'
    r'(?:(?P<andenes>Andenes)\s+|superficie\s+)?'
    r'(?P<level>[+-]?\d(?:\.\d{1,2})?)',
    re.IGNORECASE,
)
```

Grupos capturados: `line` (opcional), `andenes` (opcional), `level` (índice numérico).
Si `line` está ausente se usa `unique_route`; si también es `None` se lanza `ValueError`.

### Bandas de nivel (`LevelMixin._get_limit_levels`)

Las flechas `right_arrow` dividen el frame en bandas horizontales:
```
banda_i = {'top': y_flecha_i-1, 'bottom': y_flecha_i}
```
Primer banda: top=0 (tope del frame). Última: bottom=frame.geometry.height.

`_find_level_for_y(item_y, line)` ubica un ítem en su banda; si no cae en ninguna
toma la banda cuyo centro es más cercano.

### level_id generado

```python
# LevelMixin._make_level_id
f'{station_slug}-{line}-{suffix}'
# suffix = f'ANDENES{idx}' si has_andenes, si no str(idx)
# Ej: 'MIXCOAC-L7-ANDENES-3' / 'MIXCOAC-L12-0'
```

---

## Parsers puros (`parsers.py`)

| Función               | Descripción                                              |
|-----------------------|----------------------------------------------------------|
| `_strip_html(html)`   | Sustituye cada tag por un espacio (dos `<p>` seguidos no se pegan) y colapsa espacios |
| `_parse_content(html)`| `{name, desc, is_closed, is_double, direction}` de un shape |
| `_is_in_progress(t)`  | `True` si el título de frame termina en «(en proceso)»   |
| `_normalize_title(t)` | Sin acentos, casefold, un solo espacio: para emparejar frames con `Stop` |
| `_direction_text(n)`  | Texto tras la flecha de un rótulo de andén (`L3 <= Universidad` → `Universidad`) |
| `_get_line_prefix(t)` | Extrae prefijo de línea (`L7`, `L12A`, …) del texto     |
| `_resolve_line(item)` | Aplica `_get_line_prefix` al `data.content` de un ítem  |
| `_item_center(item)`  | `(x, y)` del centro del ítem                            |
| `_slugify(text)`      | Normaliza texto a mayúsculas ASCII sin tildes/espacios (ids, no títulos) |

`_parse_content` extrae:
- `name`: texto sin paréntesis ni corchetes
- `desc`: contenido entre paréntesis (unido con `"; "`)
- `is_closed`: `True` si aparece `[CLAUSURADA]`, `[CLAUSURADO]`, `[INHABILITADA]` o `[INHABILITADO]`
- `is_double`: `True` si aparece `[IZQ/DER]` o `[IZQ & DER]` (solo corchetes, solo en ese orden)
- `direction`: `exit` si `[salida]`, `entrance` si `[entrada]`, si no `None`

Convención del tablero: los corchetes clasifican y nunca llegan a `name` ni a `desc`; los paréntesis describen. Una marca entre paréntesis no se interpreta; un corchete no reconocido se descarta sin aviso.

`Stop.entrance` de los andenes no sale del parser sino de `assign_platform_entrances` en `stop_mixin.py` (función pura a nivel de módulo, reglas de terminal y andén central en su docstring; ver `api/CLAUDE.md`). Los shapes cuyo texto empieza con prefijo de otro sistema (`STE`) se saltan con motivo `other transit system`.

Comandos auxiliares: `dump_miro_raw` (volcado JSON de todos los frames, solo lectura) y `apply_miro_edits --edits PATH [--apply]` (PATCH de `data.content` de shapes y `data.title` de frames; simula por defecto y relee cada ítem antes de escribir). El token en `.env` tiene alcance `boards:write`.

---

## Flujo de datos en MiroSchemaBuilder (`builder.py`)

```
Frame
 ├─ type=text         → LevelMixin._parse_level_texts()
 │                         → _level_texts: {line: [{top,bottom,index,has_andenes}]}
 ├─ type=shape
 │   ├─ right_arrow   → LevelMixin._get_limit_levels()  → bandas Y del frame
 │   ├─ round_rect    → StopMixin._create_stops()        → Stop(loc_type=0)
 │   ├─ rectangle     → StopMixin._create_stops()        → Stop(loc_type=2)
 │   └─ circle        → StopMixin._create_stops()        → Stop(loc_type=3)
 └─ type=connector    → PathwayMixin._create_pathways()  → Pathway
```

### Diferencias dry_run vs normal

En `dry_run=True` los pathways usan IDs temporales con prefijo `miro:`:
```python
{
  'pathway_id': '(miro:{start_id})--(miro:{end_id})',
  'from_stop':  'miro:{start_id}',
  'to_stop':    'miro:{end_id}',
}
```
En modo normal, `from_stop`/`to_stop` son los `stop_id` reales de la BD.

---

## Previsualización del schema

Antes de guardar en la BD, verifica visualmente lo que se insertaría con:

```bash
python manage.py preview_miro_schema <frame_title>
python manage.py preview_miro_schema Mixcoac
python manage.py preview_miro_schema Mixcoac --output /tmp/mixcoac.html
```

Genera un HTML standalone (`<frame>_preview.html` por defecto) con:

- **Grafo interactivo** (Cytoscape.js) con nodos agrupados por nivel
- **Formas de nodos** por `location_type`: rectángulo=entrada, rect-redondeado=plataforma, elipse=nodo
- **Color de aristas** por `pathway_mode`: púrpura=escalera mecánica, azul=ascensor, verde=movedizo, grises=pasillo/escaleras
- **Borde rojo punteado** en nodos clausurados
- **Click en nodo/arista** → panel lateral con todos los atributos (`stop_id`, `miro_id`, `pathway_mode`, etc.)
- **Tabla de skipped** con los elementos que no se pudieron procesar y el motivo

Archivos involucrados:
- `stop/management/commands/preview_miro_schema.py` — management command
- `utils/miro/preview_html.py` — `build_cytoscape_elements()` + `render_html()`
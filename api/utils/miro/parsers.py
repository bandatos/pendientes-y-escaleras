"""Pure text-parsing helpers for Miro item content (no DB, no I/O)."""
import html
import re
import unicodedata


_LINE_RE = re.compile(r'^(L(?:\d{1,2}|[AB]))\b')
# Convención del tablero: los corchetes clasifican ([CLAUSURADA], [IZQ/DER]),
# los paréntesis describen y van a stop_desc. Solo IZQ antes de DER.
_DOUBLE_RE = re.compile(r'\[\s*IZQ\s*(?:&|/)\s*DER\s*\]', re.IGNORECASE)
# El tablero lo escriben varias manos: CLAUSURADA/O e INHABILITADO/A son
# la misma marca.
_CLOSED_RE = re.compile(
    r'\[\s*(?:CLAUSURAD[AO]|INHABILITAD[AO])\s*\]', re.IGNORECASE)
# Medido sobre el volcado completo del tablero: un solo andén de otro
# sistema, «STE-L10 <= Central» en Constitución de 1917. Se descarta porque
# no es de este inventario y porque, contado como andén de L8, rompía la
# regla de terminal de la que salen los `entrance`. Los *accesos* de otros
# sistemas no llevan prefijo y sí se importan: ver task-24 b.
_OTHER_SYSTEMS_RE = re.compile(r'^STE\b', re.IGNORECASE)
_DIRECTION_RE = re.compile(r'\[\s*(entrada|salida)\s*\]', re.IGNORECASE)
_DIRECTION_VALUES = {'entrada': 'entrance', 'salida': 'exit'}
# Sufijo con el que el tablero marca los frames aún sin terminar.
_IN_PROGRESS_RE = re.compile(r'\(\s*en\s+proceso\s*\)\s*$', re.IGNORECASE)
# Los andenes se rotulan «L3 <= Universidad»; la flecha puede ser
# <=, => o <=> (andén central) y a veces se escribe con un solo =.
_ARROW_RE = re.compile(r'<=>|<=|=>|=')
_OLD_LEVEL_TEXT_RE = re.compile(
    r'(L(?:\d{1,2}|[AB]))\s+NIVEL\s+(ANDENES\s+)?([-\d]+|SUPERFICIE\s+\d+)',
    re.IGNORECASE,
)
_LEVEL_TEXT_RE = re.compile(
    r'(?:(?P<line>L(?:\d{1,2}|[AB]))\s+)?'
    r'NIVEL\s+'
    r'(?:(?P<andenes>Andenes)\s+|superficie\s+)?'
    r'(?P<level>[+-]?\d(?:\.\d{1,2})?)',
    re.IGNORECASE,
)


def _strip_html(content: str) -> str:
    text = re.sub(r'<br[^>]*/?>|<br>', ' ', content, flags=re.IGNORECASE)
    # Con espacio, no vacío: los bloques <p> adyacentes son líneas
    # distintas del rótulo y sin él se pegarían («Acceso»+«domo»).
    text = re.sub(r'</?[a-zA-Z][^>]*>', ' ', text)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def _parse_content(content: str) -> dict:
    """Returns {name, desc, is_closed, is_double, direction} from shape HTML."""
    text = _strip_html(content)
    paren_parts = re.findall(r'\(([^)]+)\)', text)
    desc = '; '.join(paren_parts) if paren_parts else None
    is_closed = bool(_CLOSED_RE.search(text))
    is_double = bool(_DOUBLE_RE.search(text))
    direction_match = _DIRECTION_RE.search(text)
    direction = (
        _DIRECTION_VALUES[direction_match.group(1).lower()]
        if direction_match else None
    )
    name = re.sub(r'\s*\([^)]*\)', '', text)
    name = re.sub(r'\s*\[[^]]*\]', '', name).strip()
    return {
        'name': name, 'desc': desc,
        'is_closed': is_closed, 'is_double': is_double,
        'direction': direction,
    }


def _is_other_system(item: dict) -> bool:
    """True when a shape belongs to a transit system other than the Metro."""
    content = item.get('data', {}).get('content', '')
    return bool(_OTHER_SYSTEMS_RE.match(_strip_html(content)))


def _is_in_progress(title: str) -> bool:
    """True when a frame title carries the '(en proceso)' suffix."""
    return bool(_IN_PROGRESS_RE.search(title or ''))


def _normalize_title(text: str) -> str:
    """Accent-free, case-free, single-spaced form for title matching."""
    text = unicodedata.normalize('NFD', text or '')
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', text).casefold().strip()


def _direction_text(name: str) -> str | None:
    """Returns the destination written after the arrow of a platform label."""
    parts = _ARROW_RE.split(name, maxsplit=1)
    if len(parts) < 2:
        return None
    return parts[1].strip() or None


def _get_line_prefix(text: str) -> str | None:
    m = _LINE_RE.match(text.strip())
    return m.group(1) if m else None


def _resolve_line(item: dict) -> str | None:
    content = _strip_html(item.get('data', {}).get('content', ''))
    return _get_line_prefix(content)


def _item_center(item: dict) -> tuple[float, float]:
    """Returns (x, y) center. position.origin='center' → x,y is the center."""
    pos = item.get('position', {})
    return pos.get('x', 0.0), pos.get('y', 0.0)


def _slugify(text: str) -> str:
    text = unicodedata.normalize('NFD', text.upper())
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Z0-9]', '', text)
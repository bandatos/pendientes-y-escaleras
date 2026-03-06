"""Pure text-parsing helpers for Miro item content (no DB, no I/O)."""
import re
import unicodedata


_LINE_RE = re.compile(r'^(L\d{1,2}[AB]?)\b')
_OLD_LEVEL_TEXT_RE = re.compile(
    r'(L\d{1,2}[AB]?)\s+NIVEL\s+(ANDENES\s+)?([-\d]+|SUPERFICIE\s+\d+)',
    re.IGNORECASE,
)
_LEVEL_TEXT_RE = re.compile(
    r'(?:(?P<line>L\d{1,2}[AB]?)\s+)?'
    r'NIVEL\s+'
    r'(?:(?P<andenes>Andenes)\s+|superficie\s+)?'
    r'(?P<level>[+-]?\d(?:\.\d{1,2})?)',
    re.IGNORECASE,
)


def _strip_html(html: str) -> str:
    text = re.sub(r'<br[^>]*/?>|<br>', ' ', html, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def _parse_content(html: str) -> dict:
    """Returns {name, desc, is_closed} from a Miro shape HTML content."""
    text = _strip_html(html)
    paren_parts = re.findall(r'\(([^)]+)\)', text)
    desc = '; '.join(paren_parts) if paren_parts else None
    is_closed = bool(re.search(r'\[CLAUSURADA\]', text, re.IGNORECASE))
    name = re.sub(r'\s*\([^)]*\)', '', text)
    name = re.sub(r'\s*\[[^]]*\]', '', name)
    name = re.sub(r'\s*(?:<=>|<=|=>|=)\s*', ' ', name).strip()
    return {'name': name, 'desc': desc, 'is_closed': is_closed}


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
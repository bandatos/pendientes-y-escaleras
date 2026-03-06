"""PathwayMixin: pathway detection and creation logic for MiroSchemaBuilder."""
from __future__ import annotations
import re
from collections import defaultdict
from typing import TYPE_CHECKING
from stair.models import Pathway
from .parsers import _strip_html

if TYPE_CHECKING:
    from utils.miro.builder import MiroSchemaBuilder


class PathwayMixin:
    """Mixin that provides Pathway-related methods to MiroSchemaBuilder."""

    def _create_pathways(self: MiroSchemaBuilder) -> None:
        escalator_pairs = self._build_escalator_pairs()

        for conn in self._connectors:
            mode_id = self._get_pathway_mode(conn)
            if mode_id is None:
                print(f"Skipping connector {conn['id']} with unrecognized style")
                self._skipped.append({
                    'miro_id': conn['id'],
                    'reason': 'unrecognized style for pathway mode',
                })
                continue

            start_id = conn.get('startItem', {}).get('id')
            end_id = conn.get('endItem', {}).get('id')
            if not start_id or not end_id:
                self._skipped.append({
                    'miro_id': conn['id'],
                    'reason': 'connector missing endpoint',
                })
                continue

            from_stop = self._get_stop_for_miro_id(start_id)
            to_stop = self._get_stop_for_miro_id(end_id)
            if not from_stop or not to_stop:
                self._skipped.append({
                    'miro_id': conn['id'],
                    'reason': (
                        f'stop not found for miro_id {start_id} or {end_id}'
                    ),
                })
                continue

            is_bidir = self._get_bidirectional(conn, mode_id, escalator_pairs)

            from_stop, to_stop, is_bidir = self._resolve_direction(
                conn, from_stop, to_stop, mode_id, is_bidir,
                start_id, end_id,
            )

            description = self._extract_description(conn)

            obj, _ = Pathway.objects.get_or_create(
                pathway_id=conn['id'],
                defaults={
                    'miro_id': conn['id'],
                    'from_stop': from_stop,
                    'to_stop': to_stop,
                    'pathway_mode': self._get_mode(mode_id),
                    'is_bidirectional': is_bidir,
                    'pathway_description': description,
                }
            )
            self._pathway_objs.append(obj)

    def _get_pathway_mode(self: MiroSchemaBuilder, connector: dict) -> int | None:
        style = connector.get('style', {})
        color = style.get('strokeColor', '').lower()
        start_cap = style.get('startStrokeCap', 'none')
        end_cap = style.get('endStrokeCap', 'none')

        if style.get('strokeStyle') == 'dashed':
            return None
        if color == '#6631d7':
            return 4  # Escalator
        if color == '#305bab':
            return 5  # Elevator
        if color == '#067429':
            return 3  # Moving sidewalk
        if color == '#b0b0b0':
            if start_cap == 'oval' and end_cap == 'oval':
                return 1  # Walkway
            return 2  # Stairs
        return None

    def _build_escalator_pairs(self) -> dict[frozenset, list]:
        pairs: dict[frozenset, list] = defaultdict(list)
        for conn in self._connectors:
            if self._get_pathway_mode(conn) != 4:
                continue
            start_id = conn.get('startItem', {}).get('id')
            end_id = conn.get('endItem', {}).get('id')
            if start_id and end_id:
                pairs[frozenset([start_id, end_id])].append(conn)
        return dict(pairs)

    def _get_bidirectional(
        self: MiroSchemaBuilder, connector: dict, mode: int, escalator_pairs: dict,
    ) -> int:
        if mode in (1, 5):  # Walkway, Elevator
            return 1
        if mode == 3:        # Moving sidewalk
            return 0

        # Stairs: unidirectional if one cap is 'none'
        style = connector.get('style', {})
        if (style.get('startStrokeCap') == 'none'
                or style.get('endStrokeCap') == 'none'):
            return 0
        return 1

    def _resolve_direction(
        self: MiroSchemaBuilder,
        connector: dict,
        from_stop,
        to_stop,
        mode_id: int,
        is_bidir: int,
        start_miro_id: str,
        end_miro_id: str,
    ) -> tuple:
        """Aplica reglas de dirección canónica al par from_stop/to_stop.

        Regla 1 (todos los modos): si endStrokeCap='none' y startStrokeCap
        tiene valor, el conector apunta al revés → invertir stops y marcar
        como unidireccional.

        Regla 2 (mode 4, bidir): escaleras eléctricas bidireccionales se
        guardan siempre de arriba (mayor level_index) hacia abajo.
        """
        style = connector.get('style', {})
        start_cap = style.get('startStrokeCap', 'none')
        end_cap = style.get('endStrokeCap', 'none')

        # Regla 1: flecha apunta de endItem a startItem → invertir
        if end_cap == 'none' and start_cap != 'none':
            return to_stop, from_stop, 0

        # Regla 2: escaleras eléctricas bidir → canónico de arriba a abajo
        if mode_id == 4 and is_bidir == 1:
            from_stop, to_stop = self._orient_escalator_top_down(
                from_stop, to_stop, start_miro_id, end_miro_id,
            )

        return from_stop, to_stop, is_bidir

    def _orient_escalator_top_down(
        self: MiroSchemaBuilder,
        from_stop,
        to_stop,
        from_miro_id: str,
        to_miro_id: str,
    ) -> tuple:
        """Garantiza que from_stop sea el piso más alto (mayor level_index).

        Usa la coordenada Y del canvas de Miro como fallback si level_index
        no está disponible o ambos stops comparten el mismo nivel.
        Menor Y en Miro = más arriba físicamente = from_stop.
        """
        from_idx = getattr(
            getattr(from_stop, 'level', None), 'level_index', None,
        )
        to_idx = getattr(
            getattr(to_stop, 'level', None), 'level_index', None,
        )

        if from_idx is not None and to_idx is not None and from_idx != to_idx:
            if from_idx < to_idx:
                return to_stop, from_stop
            return from_stop, to_stop

        # Fallback: menor Y en canvas = piso más alto = from_stop
        from_y = self._item_y_map.get(from_miro_id, 0)
        to_y = self._item_y_map.get(to_miro_id, 0)
        if from_y > to_y:
            return to_stop, from_stop
        return from_stop, to_stop

    @staticmethod
    def _extract_description(connector: dict) -> str | None:
        parts = []
        for caption in connector.get('captions', []):
            text = _strip_html(caption.get('content', ''))
            parts.extend(re.findall(r'\(([^)]+)\)', text))
        return '; '.join(parts) if parts else None

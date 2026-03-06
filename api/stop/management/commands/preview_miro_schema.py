"""Management command: genera un HTML visual del schema Miro."""
import os

from django.core.management.base import BaseCommand, CommandError

from stop.models import Level, Stop
from stair.models import Pathway
from utils.miro.builder import MiroSchemaBuilder
from utils.miro.preview_html import build_cytoscape_elements, render_html


class Command(BaseCommand):
    """Genera un HTML con el grafo de niveles/stops/pathways de un frame Miro.

    Por defecto consulta la API de Miro y escribe los registros en la BD.
    Con ``--from-db`` usa los datos ya guardados (sin llamar a Miro).

    Uso::

        python manage.py preview_miro_schema Mixcoac
        python manage.py preview_miro_schema Mixcoac --from-db
        python manage.py preview_miro_schema Mixcoac --output /tmp/out.html
    """

    help = (
        "Genera un HTML visual con el schema de un frame Miro. "
        "Usa --from-db para leer datos ya guardados sin llamar a Miro."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "frame_title",
            type=str,
            help="Título exacto del frame en Miro (ej: 'Mixcoac').",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help=(
                "Ruta del archivo HTML de salida. "
                "Por defecto: <frame_title>_preview.html en el dir actual."
            ),
        )
        parser.add_argument(
            "--from-db",
            action="store_true",
            default=False,
            help=(
                "Lee los datos ya guardados en la BD en lugar de "
                "consultar la API de Miro. Requiere que existan Pathways "
                "asociados a la estación."
            ),
        )

    def handle(self, *args, **options) -> None:
        frame_title: str = options["frame_title"]
        output_path: str | None = options["output"]
        from_db: bool = options["from_db"]

        if output_path is None:
            slug = frame_title.lower().replace(" ", "_")
            output_path = os.path.abspath(f"{slug}_preview.html")

        if from_db:
            result = self._load_from_db(frame_title)
        else:
            self.stdout.write(
                f"Procesando frame '{frame_title}' desde Miro…"
            )
            result = MiroSchemaBuilder(frame_title).run()
            if result is None:
                raise CommandError(
                    f"No se pudo procesar el frame '{frame_title}'. "
                    "Verifica que exista en Miro y que haya stops en la BD."
                )

        levels = result.get("levels", [])
        stops = result.get("stops", [])
        pathways = result.get("pathways", [])
        skipped = result.get("skipped", [])

        self.stdout.write(
            f"  Niveles:   {len(levels)}\n"
            f"  Stops:     {len(stops)}\n"
            f"  Pathways:  {len(pathways)}\n"
            f"  Skipped:   {len(skipped)}"
        )

        elements = build_cytoscape_elements(result)
        html = render_html(elements, frame_title, skipped=skipped)

        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(html)

        self.stdout.write(
            self.style.SUCCESS(f"\nHTML generado: {output_path}")
        )

    def _load_from_db(self, frame_title: str) -> dict:
        """Carga Level/Stop/Pathway ya guardados desde la BD.

        Raises:
            CommandError: si no hay stops o Pathways para la estación.
        """
        from api.views.stop.serializers import LevelSerializer, StopCatSerializer
        from api.views.stair.serializers import PathwaySerializer

        self.stdout.write(
            f"Cargando '{frame_title}' desde la BD…"
        )

        station_stops = Stop.objects.filter(
            stop_name__iexact=frame_title)
        if not station_stops.exists():
            raise CommandError(
                f"No se encontraron stops con nombre '{frame_title}' en la BD."
            )

        child_stops = Stop.objects.filter(
            parent_station__in=station_stops)

        if not Pathway.objects.filter(
                from_stop__in=child_stops).exists():
            raise CommandError(
                f"No hay Pathways guardados para '{frame_title}'. "
                "Ejecuta sin --from-db primero."
            )

        levels = Level.objects.filter(
            stops__in=child_stops).distinct()
        pathways = Pathway.objects.filter(from_stop__in=child_stops)

        return {
            "levels": LevelSerializer(levels, many=True).data,
            "stops": StopCatSerializer(child_stops, many=True).data,
            "pathways": PathwaySerializer(pathways, many=True).data,
            "skipped": [],
        }
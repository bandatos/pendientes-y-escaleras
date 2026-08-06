"""Management command: genera un HTML visual del schema Miro."""
import csv
import os
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from stop.models import Level, Stop
from stair.models import Pathway
from utils.miro.builder import MiroSchemaBuilder
from utils.miro.preview_html import build_cytoscape_elements, render_html


class Command(BaseCommand):
    """Genera un HTML con el grafo de niveles/stops/pathways de un frame Miro.

    Por defecto consulta la API de Miro y escribe los registros en la BD.
    Con ``--from-db`` usa los datos ya guardados (sin llamar a Miro).
    Con ``--all-stations`` procesa todos los frames de Miro que tengan
    un Stop con location_type_id=1 en la BD.

    Uso::

        python manage.py preview_miro_schema Mixcoac
        python manage.py preview_miro_schema Mixcoac --reset
        python manage.py preview_miro_schema Mixcoac --from-db
        python manage.py preview_miro_schema Mixcoac --output /tmp/out.html
        python manage.py preview_miro_schema --all-stations
        python manage.py preview_miro_schema --all-stations --reset
        python manage.py preview_miro_schema --all-stations --from-db
    """

    help = (
        "Genera un HTML visual con el schema de un frame Miro. "
        "Usa --from-db para leer datos ya guardados sin llamar a Miro. "
        "Usa --all-stations para procesar todas las estaciones de Miro."
    )

    # Columnas del CSV de resumen
    _CSV_FIELDS = [
        "estacion", "estado", "niveles", "stops",
        "pathways", "skipped_count", "miro_id", "motivo",
        "comentarios",
    ]

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "frame_title",
            type=str,
            nargs="?",
            default=None,
            help="Título exacto del frame en Miro (ej: 'Mixcoac').",
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help=(
                "Ruta del archivo HTML de salida. "
                "Por defecto: media/miro_previews/<frame_title>_preview.html."
                " Ignorado si se usa --all-stations."
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
        parser.add_argument(
            "--reset",
            action="store_true",
            default=False,
            help=(
                "Elimina todos los Stops (con miro_id), Levels y Pathways "
                "de la estación antes de importar desde Miro. "
                "Con --all-stations, aplica el reset a todas las estaciones." # mejor que aplique el rese estacion por estacion solo si la importacion es correcta
            ),
        )
        parser.add_argument(
            "--all-stations",
            action="store_true",
            default=False,
            help=(
                "Procesa todos los frames de Miro que tengan un Stop con "
                "location_type_id=1 en la BD. Sin --reset, omite las que ya "
                "tienen stops importados desde Miro. Con --reset, elimina y "
                "reimporta todas."
            ),
        )

    def handle(self, *args, **options) -> None:
        frame_title: str | None = options["frame_title"]
        all_stations: bool = options["all_stations"]
        self._run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._csv_rows: list[dict] = []

        if not frame_title and not all_stations:
            raise CommandError(
                "Debes proporcionar un frame_title o usar --all-stations."
            )

        if all_stations:
            if options["from_db"] and options["reset"]:
                raise CommandError(
                    "--from-db y --reset no pueden usarse juntos."
                )
            self._handle_all_stations(
                reset=options["reset"], from_db=options["from_db"]
            )
            return

        output_path: str | None = options["output"] or self._default_output(
            frame_title
        )
        from_db: bool = options["from_db"]
        reset: bool = options["reset"]

        if from_db:
            result = self._load_from_db(frame_title)
        else:
            self.stdout.write(
                f"Procesando frame '{frame_title}' desde Miro…"
            )
            result = MiroSchemaBuilder(frame_title).run(reset_bd=reset)
            if result is None:
                raise CommandError(
                    f"No se pudo procesar el frame '{frame_title}'. "
                    "Verifica que exista en Miro y que haya stops en la BD."
                )

        self._write_preview(frame_title, result, output_path)
        self._write_csv_summary()

    # ------------------------------------------------------------------
    # All-stations batch processing
    # ------------------------------------------------------------------

    def _handle_all_stations(
        self, reset: bool, from_db: bool
    ) -> None:
        """Procesa todos los frames/estaciones según el modo indicado.

        from_db=True:  genera previews desde BD para estaciones con Pathways.
        from_db=False, reset=False: importa desde Miro solo estaciones nuevas.
        from_db=False, reset=True:  reimporta todas desde Miro con reset.
        """
        if from_db:
            self._handle_all_from_db()
            return

        from utils.miro.frames import get_all_frames

        self.stdout.write("Obteniendo frames de Miro…")
        frames = get_all_frames()

        station_names_lower = {
            name.lower()
            for name in Stop.objects.filter(
                location_type_id=1
            ).values_list("stop_name", flat=True)
        }

        matched = [
            f for f in frames
            if f.get("data", {}).get("title", "").lower()
            in station_names_lower
        ]

        mode = "RESET" if reset else "NUEVAS"
        self.stdout.write(
            f"Frames en Miro: {len(frames)} | "
            f"Con Stop en BD: {len(matched)} | "
            f"Modo: {mode}\n"
        )

        successes: list[str] = []
        skipped_list: list[str] = []
        failures: list[tuple[str, str]] = []

        for frame in matched:
            title = frame["data"]["title"]
            has_miro_data = Stop.objects.filter(
                miro_id__isnull=False,
                parent_station__stop_name__iexact=title,
            ).exists()

            if has_miro_data and not reset:
                self.stdout.write(f"  [SKIP]  {title}")
                skipped_list.append(title)
                self._csv_rows.append(self._station_row(title, "SKIP"))
                continue

            label = "[RESET]" if has_miro_data else "[NUEVO]"
            self.stdout.write(f"  {label} {title}…")

            try:
                result = MiroSchemaBuilder(title).run(
                    reset_bd=has_miro_data, frame=frame
                )
                if result is None:
                    err = "Frame o stops no encontrados en Miro/BD"
                    failures.append((title, err))
                    self._csv_rows.append(
                        self._station_row(title, "ERROR", motivo=err)
                    )
                    continue
                output_path = self._default_output(title)
                self._write_preview(title, result, output_path)
                successes.append(title)
            except Exception as exc:
                failures.append((title, str(exc)))
                self._csv_rows.append(
                    self._station_row(title, "ERROR", motivo=str(exc))
                )
                self.stderr.write(f"    ERROR: {exc}")

        self._print_summary(successes, skipped_list, failures)
        self._write_csv_summary()

    def _handle_all_from_db(self) -> None:
        """Genera previews desde la BD para todas las estaciones con Pathways."""
        station_stops = Stop.objects.filter(
            location_type_id=1,
            child_stops__miro_id__isnull=False,
            child_stops__pathways_from__isnull=False,
        ).distinct()

        self.stdout.write(
            f"Estaciones con datos en BD: {station_stops.count()}\n"
        )

        successes: list[str] = []
        failures: list[tuple[str, str]] = []

        for station in station_stops:
            title = station.stop_name
            self.stdout.write(f"  [DB] {title}…")
            try:
                result = self._load_from_db(title)
                output_path = self._default_output(title)
                self._write_preview(title, result, output_path)
                successes.append(title)
            except (CommandError, Exception) as exc:
                failures.append((title, str(exc)))
                self._csv_rows.append(
                    self._station_row(title, "ERROR", motivo=str(exc))
                )
                self.stderr.write(f"    ERROR: {exc}")

        self._print_summary(successes, [], failures)
        self._write_csv_summary()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _station_row(
        self,
        estacion: str,
        estado: str,
        *,
        niveles: int | str = "",
        stops: int | str = "",
        pathways: int | str = "",
        skipped_count: int | str = "",
        motivo: str = "",
    ) -> dict:
        """Construye una fila de resumen por estación para el CSV."""
        return {
            "estacion": estacion,
            "estado": estado,
            "niveles": niveles,
            "stops": stops,
            "pathways": pathways,
            "skipped_count": skipped_count,
            "miro_id": "",
            "motivo": motivo,
            "comentarios": "",
        }

    def _skipped_item_row(
        self, estacion: str, miro_id: str, reason: str
    ) -> dict:
        """Construye una fila de detalle por item saltado para el CSV."""
        return {
            "estacion": estacion,
            "estado": "ITEM_SALTADO",
            "niveles": "",
            "stops": "",
            "pathways": "",
            "skipped_count": "",
            "miro_id": miro_id,
            "motivo": reason,
            "comentarios": "",
        }

    def _print_summary(
        self,
        successes: list[str],
        skipped: list[str],
        failures: list[tuple[str, str]],
    ) -> None:
        self.stdout.write("\n--- Resumen ---")
        self.stdout.write(
            self.style.SUCCESS(f"OK:       {len(successes)}")
        )
        if skipped:
            self.stdout.write(f"Omitidas: {len(skipped)}")
        if failures:
            self.stdout.write(
                self.style.ERROR(f"Error:    {len(failures)}")
            )
            for title, err in failures:
                self.stderr.write(f"  {title}: {err}")

    def _write_csv_summary(self) -> None:
        """Guarda las filas acumuladas en media/miro_previews/logs/."""
        if not self._csv_rows:
            return
        logs_dir = os.path.join(
            settings.BASE_DIR, "media", "miro_previews", "logs"
        )
        os.makedirs(logs_dir, exist_ok=True)
        csv_path = os.path.join(
            logs_dir, f"resumen_import_{self._run_ts}.csv"
        )
        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self._CSV_FIELDS)
            writer.writeheader()
            writer.writerows(self._csv_rows)
        self.stdout.write(self.style.SUCCESS(f"CSV: {csv_path}"))

    def _default_output(self, frame_title: str) -> str:
        """Ruta de salida por defecto en media/miro_previews/."""
        slug = frame_title.lower().replace(" ", "_")
        previews_dir = os.path.join(
            settings.BASE_DIR, "media", "miro_previews"
        )
        os.makedirs(previews_dir, exist_ok=True)
        return os.path.join(previews_dir, f"{slug}_preview.html")

    def _write_preview(
        self, frame_title: str, result: dict, output_path: str
    ) -> None:
        """Genera y escribe el HTML de preview en output_path."""
        levels = result.get("levels", [])
        stops = result.get("stops", [])
        pathways = result.get("pathways", [])
        skipped = result.get("skipped", [])

        self.stdout.write(
            f"  Niveles:  {len(levels)}\n"
            f"  Stops:    {len(stops)}\n"
            f"  Pathways: {len(pathways)}\n"
            f"  Skipped:  {len(skipped)}"
        )

        elements = build_cytoscape_elements(result)
        html = render_html(elements, frame_title, skipped=skipped)

        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(html)

        self.stdout.write(self.style.SUCCESS(f"  HTML: {output_path}"))

        self._csv_rows.append(self._station_row(
            frame_title, "OK",
            niveles=len(levels),
            stops=len(stops),
            pathways=len(pathways),
            skipped_count=len(skipped),
        ))
        for item in skipped:
            self._csv_rows.append(self._skipped_item_row(
                frame_title, item["miro_id"], item["reason"]
            ))

    def _load_from_db(self, frame_title: str) -> dict:
        """Carga Level/Stop/Pathway ya guardados desde la BD.

        Raises:
            CommandError: si no hay stops o Pathways para la estación.
        """
        from api.views.stop.serializers import (
            LevelSerializer, StopCatSerializer)
        from api.views.stair.serializers import PathwaySerializer

        self.stdout.write(f"Cargando '{frame_title}' desde la BD…")

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

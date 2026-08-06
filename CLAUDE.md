# Pendientes y escaleras

Monorepo del relevamiento ciudadano de escaleras y elevadores del Metro de la CDMX (Bandatos). Estructura de carpetas y arranque rápido: ver `README.md`. Cada subproyecto tiene su propio `CLAUDE.md` con lo que le es específico.

## Entornos

- **`api/`**: usa siempre el intérprete del entorno virtual del subproyecto, `api/.venv/bin/python` (Python 3.14, Django 5.2.7). Nunca instales con el `pip` del sistema.
- **`vue/`**: el gestor es **yarn** y `vue/yarn.lock` es el único lockfile. Nunca corras `npm` ni `pnpm` aquí.
- Puertos de desarrollo: API en **8013** (default fijado en `api/manage.py`), Vite en **5174**. El frontend espera la API local en `:8013`.

## Commits

Prefija con `[api]` o `[vue]` los commits que tocan un solo subproyecto; sin prefijo cuando tocan la raíz, `data/`, `docs/` o ambos subproyectos. La convención viene de los dos repos originales integrados con su historia completa (`escaleras_survey_ws` → `api/`, `escalerasSurvey` → `vue/`).

## Documentación de proceso

`docs/` (tareas, decisiones/ADR, referencias, registros) está gobernado por el skill global **documenter**: no crees ni edites archivos ahí a mano, usa el skill. Un hook `pre-commit` valida la estructura antes de cada commit; `core.hooksPath` ya apunta a `.githooks/`, no hay que instalar nada.

## Datos

`data/gtfs/` es la copia canónica del GTFS; las copias bajo `api/media/` y `vue/src/assets/` son de consumo interno de cada subproyecto. Si actualizas el GTFS, actualiza la canónica y propaga, no al revés. `data/raw/` y `data/sources/` son insumos históricos: se leen, no se editan.

## Gotchas

- GitHub Pages sirve hoy `bandatos.org/pendientes-y-escaleras` desde la **raíz de `main`**, donde vivía el prototipo estático que ahora está en `prototype/`. Mergear la rama `monorepo` a `main` rompe el sitio hasta que se reconfigure: ver `docs/tasks/task-2-*` (abierta) antes de tocar el despliegue.
- El backend tiene dos modelos de escalera conviviendo (`Stair` legado y `Pathway` GTFS); un `StairReport` puede apuntar a cualquiera de los dos. No asumas uno solo desde ningún lado del stack.

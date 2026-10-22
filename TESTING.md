# Pruebas

Niveles montados, comandos y qué cubre cada uno.

## api/ — pytest + pytest-django

Configuración en `api/pytest.ini` (`--ds=core.settings`, `pythonpath = .`, archivos `tests.py`, `test_*.py` y `*_tests.py`). Intérprete siempre el del entorno virtual del subproyecto.

```bash
cd api && .venv/bin/python -m pytest utils/osm -q
```

| Suite | Archivo | Qué promete |
|---|---|---|
| Generador de .osm, soldadura | `api/utils/osm/test_weld.py` (3 pruebas, sin base de datos) | Una punta de escalera de banco no se suelda como vértice de un pasillo vecino; sin la marca sí se suelda (control que reproduce el defecto); el validador avisa si un footway pasa por una punta de banco |

`api/api/tests.py` es una suite preexistente de 16 pruebas sobre `django.test.TestCase` (usa la base de datos de prueba): hoy las 16 fallan porque `Stair()` recibe `name`, un campo que ya no existe; está registrado en [task-12](docs/tasks/task-12-higiene-tecnica-pendiente.md). `pytest` sin ruta, desde `api/`, se interrumpe en la recolección: los scripts `utils/miro/scratch/test_*.py` tocan la base al importarse («Database access not allowed»). Para correr todo hay que excluirlos:

```bash
cd api && .venv/bin/python -m pytest --ignore=utils/miro/scratch
```

No hay credenciales de prueba: la suite de `utils/osm` no toca la base de datos ni servicios externos.

## vue/ — sin suite

No hay pruebas unitarias ni e2e montadas.

## Propuestas no escritas

Las pruebas propuestas para el generador (regla de slots, bancos apilados, encaje en las hermanas, `unpinch_ring`, regresión de Portales byte a byte) están listadas en la tarea «Lo que queda del lado de Ricardo tras la sesión del 21 de octubre de 2026» (`docs/tasks/task-37-*`).

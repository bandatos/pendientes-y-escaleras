# Pendientes y escaleras

Relevamiento ciudadano del estado de escaleras eléctricas, escaleras fijas y elevadores del Metro de la Ciudad de México, impulsado por [Bandatos](https://bandatos.org). El proyecto cruza la infraestructura de accesibilidad de cada estación con datos de afluencia para visibilizar dónde pega más fuerte una escalera descompuesta.

## Estructura del monorepo

| Carpeta | Qué es |
|---|---|
| `api/` | Backend Django + DRF: modelos de estaciones, escaleras y reportes (esquema inspirado en GTFS-Pathways), importadores desde Miro y KoboToolbox, exportación a xlsx. Ver `api/README.md`. |
| `vue/` | Frontend Vue 3 + Vuetify: PWA de levantamiento en campo con soporte offline (IndexedDB) y sincronización contra la API. Ver `vue/README.md`. |
| `data/gtfs/` | Copia canónica del GTFS de transporte público de la CDMX (más la variante solo-Metro). Las copias en `api/media/` y `vue/src/assets/` son de consumo propio de cada subproyecto. |
| `data/raw/` | CSVs crudos históricos (catálogos de elevadores y escaleras, pathways, afluencia). Ya importados o superados; se conservan como fuente. |
| `data/sources/` | Insumos externos: anexos oficiales, hojas de inversión, plantillas de KoboToolbox. |
| `prototype/` | El mapa estático original (SVG + HTML), hoy publicado vía GitHub Pages. Superado funcionalmente por `vue/`, pendiente de reemplazo en el despliegue. |
| `docs/` | Documentación de proceso (tareas, decisiones/ADR, referencias, registros), gobernada por el sistema documenter. |

Este repo se formó integrando las historias completas de `bandatos/escaleras_survey_ws` (prefijo `[api]`) y `bandatos/escalerasSurvey` (prefijo `[vue]`); la convención de prefijos se mantiene para los commits nuevos que toquen un solo subproyecto.

## Arranque rápido

```bash
# API (Django) — requiere PostgreSQL y un .env basado en api/.env.template
cd api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py runserver

# Frontend (Vue) — gestor de paquetes: yarn
cd vue
yarn install
yarn dev
```

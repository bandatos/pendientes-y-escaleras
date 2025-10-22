# API y base de datos Serpientes y Escaleras (escaleras_survey_ws)
The web services to store the reports about the subway stations or 

## Pasos iniciales:
- Tener instalado Python 3, mínimo 3.13

- instalar pip (normalmente ya viene con python)

- Revisar que las variables de entorno se escribieron adecuadamente (Si se trabaja en Windows)

## Entornos virtuales
- Tener dos carpetas separadas (para una mejor organización),
- La primera para los entornos virtuales, y otro para los sistemas/proyectos

- Instalar venv
- Crear en ambiente virtual, en este caso llamado 'escaleras' en la carpeta env:
```bash
python3 -m venv ocamis
````

- Iniciar el entorno virtual (venv) en la carpeta colocada
```
# en Windows
.\escaleras\Scripts\Activate.ps1
# o en Linux/Mac
source escaleras/bin/activate
```

## Variables de entorno
- Crear un archivo .env en la carpeta dev\ocamis con las variables de entorno necesarias (puedes basarte en el archivo .env.example)

## Instalación de paquetes requeridos
- Instalar los paquetes requeridos para el sistema en la carpeta dev\ocamis.  (Esto viene en el archivo requirements.txt)
```bash
pip install -r requirements.txt
```

## Base de datos

### Opción 1: SQLite (Recomendado para desarrollo local)

**SQLite es más simple y no requiere instalación de servidor de base de datos.**

Para usar SQLite, configura tu archivo `.env` de la siguiente manera:
```env
POSTRGRESQL_DB=  # Dejar vacío o comentar esta línea
DATABASE_NAME=db.sqlite3
```

**Cambios necesarios en el código para SQLite:**
1. En `core/settings/__init__.py`, comentar la línea:
   ```python
   # 'django.contrib.postgres',  # Comentado para SQLite
   ```

2. La configuración de `DATABASE_SCHEMA` solo debe aplicarse para PostgreSQL:
   ```python
   # Only apply schema options for PostgreSQL
   if DATABASE_SCHEMA and POSTRGRESQL_DB:
       default_database['OPTIONS'] = {
           'options': f'-c search_path={DATABASE_SCHEMA}',
       }
   ```

**Dependencias adicionales necesarias:**
```bash
pip install Pillow  # Para campos de imagen
pip install unidecode  # Para el comando import_stairs
```

### Opción 2: PostgreSQL (Para producción o equipos que ya lo usan)

- Deberás tener instalado PostgreSQL
- Crear una base de datos en PostgreSQL llamada 'escaleras-local' (o el nombre que desees)
- Configurar tu archivo `.env` con las credenciales de PostgreSQL:
  ```env
  POSTRGRESQL_DB=True
  DATABASE_NAME=escaleras-local
  DATABASE_USER=tu_usuario
  DATABASE_PASSWORD=tu_contraseña
  DATABASE_HOST=localhost
  DATABASE_PORT=5432
  DATABASE_SCHEMA=public
  ```
- Descomentar `'django.contrib.postgres'` en `INSTALLED_APPS` (en `core/settings/__init__.py`) 

### Migración inicial de datos
- Si se desea migrar los datos desde la base de datos antigua, seguir los pasos indicados en el archivo migrate_data.md

### Crear las tablas en la base de datos
- Correr las migraciones iniciales con el siguiente comando:
```bash
python manage.py migrate
```
- Crear el primer usuario de la base de datos
```bash
python manage.py createsuperuser
```

### Cargar los datos iniciales

```bash
python manage.py import_routes
python manage.py import_stops
python manage.py create_stations
python manage.py import_stairs
python manage.py recover_viz_features media/estaciones-match-stops.csv

```


## Correr el servidor localmente
- Antes de correr el servicio, genera los archivos estáticos con el siguiente comando:
```bash
python manage.py collectstatic
```
- Correr el servidor localmente con el siguiente comando:
```console
python manage.py runserver
```
- Acceder a la aplicación en el navegador web en la dirección http://localhost:8013




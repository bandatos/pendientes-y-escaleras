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

- Deberás tener instalado PostgreSQL
- Crear una base de datos en PostgreSQL llamada 'escaleras-local' (o el nombre que desees, pero debe coincidir con el que se encuentra en tu archivo .env)
- Pobla todas la variables de .env con los datos correspondientes a tu base de datos y otros servicios (correo, etc) 

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




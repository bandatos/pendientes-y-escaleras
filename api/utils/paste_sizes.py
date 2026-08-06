from utils.normalizer import text_normalizer

stairs_counts = {
	"ALLENDE": 4,
	"AQUILES SERDAN	": 2,
	"ATLALILCO": 6,
	"AUDITORIO": 8,
	"BALBUENA": 3,
	"BALDERAS	": 1,
	"BARRANCA DEL MUERTO	": 0,
	"BELLAS ARTES": 7,
	"CALLE 11": 3,
	"CAMARONES	": 6,
	"CENTRO MEDICO	": 0,
	"CHABACANO	": 2,
	"CHILPANCINGO": 4,
	"CIUDAD DEPORTIVA": 2,
	"COLEGIO MILITAR": 2,
	"CONSTITUYENTES	": 2,
	"CONSULADO": 9,
	"COPILCO": 4,
	"CUAUHTEMOC": 2,
	"CUITLÁHUAC": 1,
	"CULHUACAN": 4,
	"DEPORTIVO 18 DE MARZO": 2,
	"EJE CENTRAL": 6,
	"ERMITA	": 2,
	"FRAY SERVANDO": 2,
	"GARIBALDI": 6,
	"GENERAL ANAYA": 2,
	"GOMEZ FARIAS": 2,
	"GUERRERO": 5,
	"HIDALGO	": 0,
	"HOSPITAL 20 DE NOVIEMBRE": 6,
	"HOSPITAL GENERAL": 3,
	"INSURGENTES SUR": 6,
	"ISABEL LA CATÓLICA": 2,
	"JAMAICA": 8,
	"JUAREZ": 2,
	"LA VILLA/BASILICA": 1,
	"LOMAS ESTRELLA": 4,
	"MARTIN CARRERA": 1,
	"MEXICALTZINGO": 6,
	"MIGUEL ANGEL DE QUEVEDO": 4,
	"MIXCOAC	": 9,
	"MOCTEZUMA": 2,
	"MORELOS": 4,
	"NATIVITAS": 2,
	"NOPALERA": 4,
	"NORMAL": 2,
	"OLIVOS": 4,
	"PANTITLAN": 5,
	"PARQUE DE LOS VENADOS": 6,
	"PATRIOTISMO": 4,
	"PERIFERICO": 8,
	"PINO SUÁREZ": 8,
	"POLANCO": 8,
	"POPOTLA": 1,
	"PORTALES": 2,
	"PUEBLA": 2,
	"REFINERIA": 8,
	"REVOLUCIÓN": 2,
	"SALTO DEL AGUA": 7,
	"SAN ANDRES TOMATLAN": 4,
	"SAN ANTONIO": 8,
	"SAN ANTONIO ABAD": 2,
	"SAN COSME": 2,
	"SAN JOAQUÍN	": 0,
	"SAN LÁZARO": 3,
	"SAN PEDRO DE LOS PINOS	": 0,
	"SANTA ANITA": 4,
	"SEVILLA": 2,
	"TACUBA	": 6,
	"TACUBAYA	": 4,
	"TASQUEÑA": 2,
	"TEZONCO": 3,
	"TLAHUAC": 4,
	"TLALTENCO": 3,
	"VELODROMO": 2,
	"VIADUCTO": 2,
	"VILLA DE CORTES": 2,
	"VIVEROS": 2,
	"XOLA": 2,
	"ZAPATA": 8,
	"ZAPOTITLÁN": 4,
	"ZARAGOZA": 3,
	"ZOCALO": 4
}

def similar(a, b):
    from difflib import SequenceMatcher
    if a and b:
        return SequenceMatcher(None, a, b).ratio()
    else:
        return 0


def load_from_csv():
    import csv
    import os

    new_stairs_counts = {}
    for station_name, count in stairs_counts.items():
        normalized_name = text_normalizer(station_name)
        new_stairs_counts[normalized_name] = count

    file_path = "D:/dev/open/escalerasSurvey/src/assets/datos"
    file_name = "estaciones-match-stops.csv"
    full_path = os.path.join(file_path, file_name)
    headers = ["x", "y", "class", "href", "texto", "x_texto",
               "y_texto", "text_anchor", "transform", "color"]

    ready_stations = set()
    # read csv file and update stairs count
    with open(full_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            station_text = row["texto"].strip().upper()
            station_text = text_normalizer(station_text)
            if station_text in new_stairs_counts:

                row["stairs"] = new_stairs_counts[station_text]
                ready_stations.add(station_text)
            else:
                row["stairs"] = None
                print(f"Warning: Station '{station_text}' not found in stairs_counts.")

    missing_stations = set(new_stairs_counts.keys()) - ready_stations
    if missing_stations:
        print("Warning: The following stations were not found in the CSV file:")
        for station in missing_stations:
            print(f"- {station}")

    # read the new data and save it to a new csv file
    new_file_name = "estaciones-vis-with-stairs.csv"
    new_full_path = os.path.join(file_path, new_file_name)
    with open(new_full_path, mode='w', encoding='utf-8', newline='') as new_file:
        writer = csv.DictWriter(new_file, fieldnames=headers + ["stairs"])
        writer.writeheader()
        for row in reader:
            writer.writerow(row)


    # example of stops.txt:
    # stop_id,stop_name,stop_lat,stop_lon,zone_id,wheelchair_boarding
    # 020L12-TLAHUAC,Tláhuac,19.28602,-99.0142,020L12-TLAHUAC,1

    #read stops.txt and update stairs count
    stops_file_name = "stops.txt"
    stops_full_path = os.path.join(file_path, stops_file_name)
    stops_headers = ["stop_id", "stop_name", "stop_lat", "stop_lon",
                     "zone_id", "wheelchair_boarding"]
    stops_dict = {}
    with open(stops_full_path, mode='r', encoding='utf-8') as stops_file:
        reader = csv.DictReader(stops_file)
        for row in reader:
            stop_id = row["stop_id"]
            stop_name = row["stop_name"].strip()
            stops_dict[stop_id] = stop_name

    # create a new file with the stops and the stairs count
    # stops_with_stairs_file_name = "stops-with-stairs.txt"
    # stops_with_stairs_full_path = os.path.join(file_path, stops_with_stairs_file




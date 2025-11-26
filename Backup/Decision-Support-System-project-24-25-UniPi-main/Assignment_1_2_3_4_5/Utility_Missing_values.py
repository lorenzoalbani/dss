from geopy.geocoders import Nominatim
import time
from collections import defaultdict
import csv

# LOAD DATASET
def load_csv(filepath):
    with open(filepath, mode='r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

#SAVE CSV
def save_to_csv(data, file_path):
    if not data:
        print(f"Dataset vuoto, impossibile salvare il file: {file_path}")
        return

    columns = data[0].keys()

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=columns)

        writer.writeheader()
        writer.writerows(data)
    print(f"File salvato correttamente: {file_path}")


# REPLACE NULL VALUES IN THE SPECIFIED COLUMN WITH THE SPECIFIED VALUE
def replace_nulls(ds, column_name, replacement_value):
    for record in ds:
        if column_name in record:
            value = record[column_name]
            if value is None or (isinstance(value, str) and value.strip().lower() in ["", "null", "none"]):
                record[column_name] = replacement_value
    return ds


# REPLACE NULL VALUES IN THE SPECIFIED COLUMN WITH THE SPECIFIED VALUE IF ANOTHER COLUMN HAS A SPECIFIC VALUE
def replace_nulls_with_conditions(ds, column_name_to_check, target_value, column_to_replace, replacement_value):
    for record in ds:
        if record.get(column_name_to_check) == target_value and not record.get(column_to_replace):
            record[column_to_replace] = replacement_value
    return ds

# FUNZIONE PER APPLICARE LE SOSTITUZIONI
def apply_replacements(dataset, replacements_dict, column_check):
    for column, conditions in replacements_dict.items():
        for unit_type, replacement_value in conditions.items():
            dataset = replace_nulls_with_conditions(dataset, column_check, unit_type, column, replacement_value)
    return dataset


# FUNCTIONS TO FILL GEOLOCATION
geolocator = Nominatim(user_agent="incident_locator")

def fill_missing_geolocation(data, street_no_col, street_dir_col, street_name_col, lat_col, lon_col, loc_col,
                             city="Chicago", state="IL", pause=1):

    # Funzione interna per geocodificare un indirizzo
    def get_lat_lon_location(street_no, street_direction, street_name):
        try:
            address = f"{street_no} {street_direction} {street_name}, {city}, {state}"
            location = geolocator.geocode(address, timeout=10) # viene assegnato il valore della location usando geolocator.geocode
            if location:
                return location.latitude, location.longitude, location.address
        except Exception as e:
            print(f"Errore con l'indirizzo {address}: {e}")
        return None

    for record in data:
        if not record.get(lat_col) or not record.get(lon_col) or not record.get(loc_col):
            result = get_lat_lon_location(record.get(street_no_col), record.get(street_dir_col),
                                          record.get(street_name_col))
            if result:
                lat, lon, loc = result
                if lat and lon:

                    record[lat_col] = lat
                    record[lon_col] = lon
                    record[loc_col] = loc

            time.sleep(pause)

    return data

# we don't use this function bc we already had the dict
def calculate_mean_coordinates(dataset, street_name, latitude, longitude):

    street_coordinates = defaultdict(list)

    for row in dataset:
        street_name = row.get(street_name)
        latitude = row.get(latitude)
        longitude = row.get(longitude)

        if street_name and latitude is not None and longitude is not None:
            street_coordinates[street_name].append((latitude, longitude))

    #compute mean for each row
    street_mean_coordinates = {}
    for street_name, coords in street_coordinates.items():
        if coords:
            avg_latitude = sum(coord[0] for coord in coords) / len(coords)
            avg_longitude = sum(coord[1] for coord in coords) / len(coords)
            street_mean_coordinates[street_name] = {
                'latitude': avg_latitude,
                'longitude': avg_longitude
            }

    return street_mean_coordinates

# CHECK IF THERE ARE NULL VALUES

def check_null_values(data):
    null_counts = {}

    null_values = [None, "", " ", "null", "none", "nan", "NaN"]

    for row in data:
        for column, value in row.items():
            if value in null_values:
                null_counts[column] = null_counts.get(column, 0) + 1

    return "Valori: ", null_counts
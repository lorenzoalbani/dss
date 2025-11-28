# from collections import defaultdict
from Utility_Missing_values import replace_nulls, apply_replacements, replace_nulls_with_conditions, fill_missing_geolocation, check_null_values, load_csv, save_to_csv
vehicles = load_csv('C:/Users/al797/DSS LAB/Vehicles.csv')
crashes = load_csv('C:/Users/al797//DSS LAB/Crashes.csv')
people = load_csv('C:/Users/al797/DSS LAB/People.csv')

##########################################################################
############################ CRASHES DATASET #############################
##########################################################################


crashes = replace_nulls(crashes, 'STREET_NAME', '76TH ST')

crashes = replace_nulls(crashes, 'MOST_SEVERE_INJURY', 'NO INDICATION OF INJURY')

crashes = replace_nulls(crashes, 'REPORT_TYPE', 'NOT ON SCENE (DESK REPORT)')

replacements_crashes_street_name = {
    'STREET_DIRECTION': {
        'DOTY AVE W': 'S',
        'BESSIE COLEMAN DR': 'N',
    },

    'BEAT_OF_OCCURRENCE': {
        'BESSIE COLEMAN DR': 1654.0,
    }
}
replacements_crashes_location = {
'BEAT_OF_OCCURRENCE': {
    'POINT (-87.614552135332 41.780148264311)': 312.0,
    'POINT (-87.653621088745 41.786811402722)': 712.0,
    'POINT (-87.713896783814 41.994542305274)': 1711.0,
},
}

crashes = apply_replacements(crashes, replacements_crashes_street_name, 'STREET_NAME')

crashes = apply_replacements(crashes, replacements_crashes_street_name, 'LOCATION')

crashes = apply_replacements(crashes, replacements_crashes_location, 'LOCATION')

crashes = fill_missing_geolocation(crashes, 'STREET_NO', 'STREET_DIRECTION', 'STREET_NAME', 'LATITUDE', 'LONGITUDE', 'LOCATION')


#### Per i null values che con GeoPy non siamo riusciti a fillare, abbiamo creato un dizionario che, per ogni strada che non ha lat e log,
#### riporta la media di latitudine e longitudine per i record riferiti alla stessa strada che hanno la location.

street_mean_coordinates = {

    'CHICAGO SKYWAY OB': {'latitude': 41.74227883457143, 'longitude': -87.57590929792856},
    'CHICAGO SKYWAY IB': {'latitude': 41.74227353683332, 'longitude': -87.57654492987038},
    'OHARE ST': {'latitude': 41.97620113900001, 'longitude': -87.90530912500004},
    'KENNEDY EXPY IB': {'latitude': 41.9445149038, 'longitude': -87.74905055459999},
    'MC FETRIDGE DR': {'latitude': 41.865043402551734, 'longitude': -87.6173671586207},
    'RANDOLPH SUB ST': {'latitude': 41.884592989666665, 'longitude': -87.62160521266667},
    'LA SALLE DR': {'latitude': 41.90103851500532, 'longitude': -87.63245768456915},
    'MANNHEIM RD': {'latitude': 41.98863609599999, 'longitude': -87.8821597974},
    'SOUTH WATER RAMP': {'latitude': 41.886845844999996, 'longitude': -87.621254377},
    'KENNEDY EXPY OB': {'latitude': 41.953580825, 'longitude': -87.7301759305},
    '87TH ST': {'latitude': 41.73621988185685, 'longitude': -87.6337419882137},
    'KEDVALE AVE': {'latitude': 41.87563567062, 'longitude': -87.72905901827599},
    'LAKE SHORE DR NB': {'latitude': 41.899861723909424, 'longitude': -87.62224080009368},
    'LAKE LOWER ST': {'latitude': 41.885688421, 'longitude': -87.62097238825},
    'DOTY AVE E': {'latitude': 41.691178218063584, 'longitude': -87.59287764128324},
    'WACKER SUB DR': {'latitude': 41.888183762, 'longitude': -87.622614368}
}


for street_name, coordinates in street_mean_coordinates.items():
    latitude = coordinates['latitude']
    longitude = coordinates['longitude']

    replace_nulls_with_conditions(crashes, 'STREET_NAME', street_name, 'LATITUDE', latitude)

    replace_nulls_with_conditions(crashes, 'STREET_NAME', street_name, 'LONGITUDE', longitude)

    location_value = f"POINT({latitude} {longitude})"

    replace_nulls_with_conditions(crashes, 'STREET_NAME', street_name, 'LOCATION', location_value)

crashes = replace_nulls(crashes, 'LOCATION', 'UNKNOWN')
crashes = replace_nulls(crashes, 'LATITUDE', -1)
crashes = replace_nulls(crashes, 'LONGITUDE', -1)

##########################################################################
############################ PEOPLE DATASET ##############################
##########################################################################

replacements_people = {
    'AIRBAG_DEPLOYED' : {
        'BICYCLE': 'NOT APPLICABLE',
        'PEDESTRIAN': 'NOT APPLICABLE',
        'NON-MOTOR VEHICLE': 'NOT APPLICABLE',
        'NON-CONTACT VEHICLE': 'DEPLOYMENT UNKNOWN',
        'PASSENGER': 'DEPLOYMENT UNKNOWN',
    },

    'EJECTION' : {
        'PASSENGER': 'UNKNOWN',
        'NON-CONTACT VEHICLE': 'UNKNOWN',
        'BICYCLE': 'UNKNOWN',
        'PEDESTRIAN': 'NOT APPLICABLE',
        'NON-MOTOR VEHICLE': 'UNKNOWN',
    },

}

people =apply_replacements(people, replacements_people, 'PERSON_TYPE')

# UNIT_TYPE Replacement
people =replace_nulls(people, 'VEHICLE_ID', -1.0)

# CITY Replacement
people = replace_nulls(people, 'CITY', 'CHICAGO')

# STATE Replacement
people =replace_nulls(people, 'STATE', 'IL')

# SEX Replacement
people = replace_nulls(people, 'SEX', 'U')

# AGE Replacement (Using Median)
people =replace_nulls(people, 'AGE', 36)

# SAFETY_EQUIPMENT Replacement
people =replace_nulls(people, 'SAFETY_EQUIPMENT', 'USAGE UNKNOWN')

# INJURY_CLASSIFICATION Replacement
people =replace_nulls(people, 'INJURY_CLASSIFICATION', 'UNKNOWN INJURIES')
people =replace_nulls(people, 'DRIVER_ACTION', 'UNKNOWN')
people =replace_nulls(people, 'DRIVER_VISION', 'UNKNOWN')
people =replace_nulls(people, 'PHYSICAL_CONDITION', 'UNKNOWN')

# BAC_RESULT Replacement
people =replace_nulls(people, 'BAC_RESULT', 'UNKNOWN')

# DAMAGE Replacement
people = replace_nulls(people, 'DAMAGE', '250.00')

# Round DAMAGE to two decimal places
for record in people:
    if record["DAMAGE"]:
        try:
            record["DAMAGE"] = round(float(record["DAMAGE"]), 2)
        except ValueError:
            pass


##########################################################################
############################ VEHICLE DATASET #############################
##########################################################################


# Sostituzioni condizionali per colonne
replacements_vehicles = {
    'MAKE': {
        'PEDESTRIAN': 'NON APPLICABLE',
        'BICYCLE': 'NON APPLICABLE',
        'NON-MOTOR VEHICLE': 'NON APPLICABLE',
        'NON-CONTACT VEHICLE': 'UNKNOWN',
        'DRIVER': 'UNKNOWN',
    },

    'MODEL': {
        'PEDESTRIAN': 'NON APPLICABLE',
        'BICYCLE': 'NON APPLICABLE',
        'NON-MOTOR VEHICLE': 'NON APPLICABLE',
        'NON-CONTACT VEHICLE': 'UNKNOWN',
        'DRIVER': 'UNKNOWN',
        'PARKED': 'UNKNOWN',
        'DRIVERLESS': 'UNKNOWN',
    },

    'LIC_PLATE_STATE': {
        'PEDESTRIAN': 'NON APPLICABLE',
        'BICYCLE': 'NON APPLICABLE',
        'NON-MOTOR VEHICLE': 'NON APPLICABLE',
        'NON-CONTACT VEHICLE': 'XX',
        'DRIVER': 'XX',
        'PARKED': 'XX',
        'DRIVERLESS': 'XX',
    },

    'VEHICLE_DEFECT': {
        'PEDESTRIAN': 'NON APPLICABLE',
        'BICYCLE': 'NON APPLICABLE',
        'NON-MOTOR VEHICLE': 'NON APPLICABLE',
        'NON-CONTACT VEHICLE': 'UNKNOWN',
        'DRIVER': 'UNKNOWN',
    },

    'VEHICLE_TYPE': {
        'PEDESTRIAN': 'FEET',
        'BICYCLE': 'BICYCLE',
        'NON-MOTOR VEHICLE': 'NON-MOTOR VEHICLE',
        'NON-CONTACT VEHICLE': 'UNKNOWN',
        'DRIVER': 'UNKNOWN',
    },

    'FIRST_CONTACT_POINT': {
        'PEDESTRIAN': 'UNKNOWN',
        'BICYCLE': 'UNKNOWN',
        'NON-MOTOR VEHICLE': 'UNKNOWN',
        'NON-CONTACT VEHICLE': 'NONE',
        'DRIVER': 'UNKNOWN',
    },
}

vehicles = apply_replacements(vehicles, replacements_vehicles, 'UNIT_TYPE')

vehicles = replace_nulls(vehicles, 'VEHICLE_ID', -1.0)
vehicles = replace_nulls(vehicles, 'UNIT_TYPE', 'BICYCLE')
vehicles = replace_nulls(vehicles, 'VEHICLE_USE', 'UNKNOWN/NA')
vehicles = replace_nulls(vehicles, 'VEHICLE_YEAR', -1.0)
vehicles = replace_nulls(vehicles, 'TRAVEL_DIRECTION', 'UNKNOWN')
vehicles = replace_nulls(vehicles, 'MANEUVER', 'UNKNOWN/NA')
vehicles = replace_nulls(vehicles, 'OCCUPANT_CNT', -1.0)

#DEALING WITH THE LAST ROW STANDING
vehicles = replace_nulls(vehicles, 'MAKE', 'UNKNOWN')
vehicles = replace_nulls(vehicles, 'MODEL', 'UNKNOWN')
vehicles = replace_nulls(vehicles, 'LIC_PLATE_STATE', 'XX')
vehicles = replace_nulls(vehicles, 'VEHICLE_DEFECT', 'UNKNOWN')
vehicles = replace_nulls(vehicles, 'VEHICLE_TYPE', 'UNKNOWN')
vehicles = replace_nulls(vehicles, 'FIRST_CONTACT_POINT', 'UNKNOWN')

# Salva i dataset modificati
save_to_csv(crashes, 'C:/Users/al797/Desktop/Crashes_filled.csv')
save_to_csv(people, 'C:/Users/al797/Desktop/People_filled.csv')
save_to_csv(vehicles, 'C:/Users/al797/Desktop/Vehicles_filled.csv')

check_null_values(crashes)
check_null_values(vehicles)
check_null_values(people)
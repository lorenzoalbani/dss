# config.py

DB_CONFIG = {
    # Ho rimosso 'tcp:' davanti perché nello script del lab non c'era, 
    # ma se fallisce prova a rimetterlo: 'tcp:lds-server-2025.database.windows.net'
    'server': '131.114.50.57', 
    'database': 'Group_ID_3_DB',                   
    'username': 'Group_ID_3',
    'password': 'QUJFIYEF',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

# Percorso CSV
CSV_DIR = "csv_db"

BATCH_SIZE = 5000

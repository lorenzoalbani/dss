# config.py

DB_CONFIG = {
    # Ho rimosso 'tcp:' davanti perché nello script di Anna non c'era, 
    # ma se fallisce prova a rimetterlo: 'tcp:lds-server-2025.database.windows.net'
    'server': '131.114.50.57', # Sostituisci col tuo server
    'database': 'Group_ID_3_DB',                   # Sostituisci col tuo DB
    'username': 'Group_ID_3',
    'password': 'QUJFIYEF',
    'driver': '{ODBC Driver 17 for SQL Server}'
}

# Percorso CSV (con la r davanti per Windows)
CSV_DIR = r"C:\Users\Admin\OneDrive - University of Pisa\Desktop\uni\magistrale\LDS\exam\project\csv_db"

BATCH_SIZE = 5000
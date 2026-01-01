# db_utils.py
import pyodbc
from config import DB_CONFIG

def get_connection():
    server = DB_CONFIG['server']
    database = DB_CONFIG['database']
    username = DB_CONFIG['username']
    password = DB_CONFIG['password']
    
    # Stringa di connessione con parametri Azure obbligatori
    connectionString = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password + ';Encrypt=yes;TrustServerCertificate=yes;Connect Timeout=30;'
    
    return pyodbc.connect(connectionString)

def clean_row_for_sql(row):
    """
    Pulisce i dati grezzi del CSV:
    - Rimuove spazi extra
    - Converte stringhe vuote o 'None' in NULL
    """
    cleaned = []
    
    for val in row:
        # Toglie spazi ai lati se è stringa
        val = val.strip() if isinstance(val, str) else val
        
        # Gestione NULL
        if val == '' or val == 'None':
            cleaned.append(None)
        else:
            cleaned.append(val)
            
    return cleaned

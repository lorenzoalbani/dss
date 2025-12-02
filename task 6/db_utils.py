# db_utils.py
import pyodbc
import re
from config import DB_CONFIG

def get_connection():
    """
    Crea la connessione usando lo stile richiesto.
    """
    server = DB_CONFIG['server']
    database = DB_CONFIG['database']
    username = DB_CONFIG['username']
    password = DB_CONFIG['password']
    
    # Stringa di connessione con parametri Azure obbligatori
    connectionString = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password + ';Encrypt=yes;TrustServerCertificate=yes;Connect Timeout=30;'
    
    return pyodbc.connect(connectionString)

def clean_row_for_sql(row):
    """
    Pulisce i dati e CORREGGE LE DATE INVALIDI (Es: 2021-00-01)
    """
    cleaned = []
    
    # Regex per trovare date nel formato YYYY-MM-DD
    # Cerca stringhe che sembrano date (4 cifre - 2 cifre - 2 cifre)
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    for val in row:
        val = val.strip() if isinstance(val, str) else val
        
        if val == '' or val == 'None':
            cleaned.append(None)
        
        elif isinstance(val, str) and date_pattern.match(val):
            # --- FIX DATE CORROTTE ---
            # Se troviamo pezzi con "-00", li sostituiamo con "-01"
            # Es: "2021-00-05" diventa "2021-01-05"
            # Es: "2021-11-00" diventa "2021-11-01"
            if '-00' in val:
                fixed_date = val.replace('-00', '-01')
                cleaned.append(fixed_date)
            else:
                cleaned.append(val)
        else:
            cleaned.append(val)
            
    return cleaned
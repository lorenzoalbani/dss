# db_utils.py
import pyodbc
from config import DB_CONFIG

def get_connection():
    """Crea e restituisce la connessione al database."""
    # Costruiamo la stringa di connessione standard per Azure SQL
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        "Encrypt=yes;"                  # Necessario per Azure
        "TrustServerCertificate=no;"    # Sicurezza standard Azure
        "Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

def clean_row_for_sql(row):
    """
    Pulisce i dati grezzi del CSV prima dell'invio.
    Converte stringhe vuote o 'None' letterali in NULL SQL (None in Python).
    """
    cleaned = []
    for val in row:
        # Rimuove spazi bianchi eccessivi se è una stringa
        val = val.strip() if isinstance(val, str) else val
        
        # Gestione dei NULL
        if val == '' or val == 'None':
            cleaned.append(None)
        else:
            cleaned.append(val)
    return cleaned
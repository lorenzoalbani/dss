# db_utils.py
import pyodbc
from config import DB_CONFIG

def get_connection():
    """Crea e restituisce la connessione al database."""
    
    # Costruiamo la stringa in modo pulito e sicuro.
    # Nota: TrustServerCertificate=yes dice al driver di ignorare 
    # il fatto che il certificato del server Azure non sia nel tuo PC.
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connect Timeout=30;"
    )
    
    # Stampa di debug (senza password) per vedere cosa stiamo inviando
    # print(f"DEBUG - Stringa connessione: {conn_str.replace(DB_CONFIG['password'], '***')}")
    
    return pyodbc.connect(conn_str)

def clean_row_for_sql(row):
    """
    Pulisce i dati grezzi del CSV prima dell'invio.
    Converte stringhe vuote o 'None' letterali in NULL SQL.
    """
    cleaned = []
    for val in row:
        val = val.strip() if isinstance(val, str) else val
        if val == '' or val == 'None':
            cleaned.append(None)
        else:
            cleaned.append(val)
    return cleaned
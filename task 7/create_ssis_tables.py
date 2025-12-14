from db_utils import get_connection
import pyodbc

def duplicate_tables_for_ssis(conn):
    """
    Duplica la struttura di tutte le tabelle del Data Warehouse
    aggiungendo il suffisso '_SSIS'.
    Usa la tecnica 'SELECT * INTO ... WHERE 1=0' per copiare 
    solo le colonne e i tipi di dato, senza le righe.
    """
    
    # Lista delle tabelle originali
    tables = [
        'Dim_Time',
        'Dim_Artist',
        'Dim_Album',
        'Dim_Sound',
        'Dim_Track',
        'Dim_Youtube',
        'Bridge_Track_Artist',
        'Fact_Streams'
    ]
    
    cursor = conn.cursor()
    
    try:
        for table in tables:
            new_table = f"{table}_SSIS"
            print(f"Processing: {table} -> {new_table}...")
            
            # Cancella la tabella _SSIS se esiste già (per poter rilanciare lo script)
            # Nota: L'ordine di drop non è critico qui perché SELECT INTO non crea Foreign Keys
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {new_table}")
            except pyodbc.Error:
                # Fallback per versioni vecchie di SQL Server che non supportano "IF EXISTS"
                try:
                    cursor.execute(f"DROP TABLE {new_table}")
                except:
                    pass

            # Crea la nuova tabella copiando la struttura dalla vecchia
            # WHERE 1 = 0 assicura che non vengano copiati i dati
            sql = f"SELECT * INTO {new_table} FROM {table} WHERE 1 = 0"
            cursor.execute(sql)
            
            print(f"Creata {new_table}")

        conn.commit()

        print("Le tabelle _SSIS sono pronte e vuote.")

    except pyodbc.Error as e:
        conn.rollback()
        print(f"\n ERRORE DURANTE LA DUPLICAZIONE: {e}")
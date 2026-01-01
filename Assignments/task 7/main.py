from db_utils import get_connection
from create_ssis_tables import duplicate_tables_for_ssis

def main():
    print("Avvio procedura creazione tabelle SSIS...")
    
    try:
        # connessione
        conn = get_connection()
        print("Connessione al DB stabilita.")

        # funzione di duplicazione
        duplicate_tables_for_ssis(conn)

    except Exception as e:
        print(f"Errore critico: {e}")
    finally:
        # Chiusura connessione
        if 'conn' in locals():
            conn.close()
            print("Connessione chiusa.")

if __name__ == "__main__":
    main()
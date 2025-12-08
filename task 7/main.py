from db_utils import get_connection
from create_ssis_tables import duplicate_tables_for_ssis

def main():
    print("Avvio procedura creazione tabelle SSIS...")
    
    try:
        # 1. Ottieni la connessione (usa il tuo db_utils esistente)
        conn = get_connection()
        print("Connessione al DB stabilita.")

        # 2. Chiama la funzione di duplicazione importata
        duplicate_tables_for_ssis(conn)

    except Exception as e:
        print(f"Errore critico: {e}")
    finally:
        # 3. Chiudi sempre la connessione
        if 'conn' in locals():
            conn.close()
            print("Connessione chiusa.")

if __name__ == "__main__":
    main()
# main.py
from db_utils import get_connection
from db_loader import load_table_bulk

def main():
    print("=== DATA WAREHOUSE LOADER (Group 03) ===")
    print("Tentativo di connessione al Server Azure...")
    
    try:
        conn = get_connection()
        print("Connessione stabilita con successo!")
    except Exception as e:
        print(f"Errore fatale di connessione: {e}")
        print("Controlla user, password e firewall del server.")
        return

    # --- LISTA ORDINATA TABELLE ---
    tables_to_load = [
        # 1. Dimensioni Indipendenti
        ('dim_time.csv', 'Dim_Time'),
        ('dim_artist.csv', 'Dim_Artist'),
        ('dim_album.csv', 'Dim_Album'),
        ('dim_sound.csv', 'Dim_Sound'), # Assicurati: NO IDENTITY(1,1) in SQL
        
        # 2. Dimensioni Dipendenti
        ('dim_track.csv', 'Dim_Track'), 
        
        # 3. Bridge
        ('bridge_track_artist.csv', 'Bridge_Track_Artist'),
        
        # 4. Fact Table
        ('fact_streams.csv', 'Fact_Streams')
    ]

    try:
        for csv_file, table_name in tables_to_load:
            load_table_bulk(conn, csv_file, table_name)
        
        print("\n===========================================")
        print(" PROCESSO COMPLETATO: DB Aggiornato!")
        print("===========================================")

    except Exception as e:
        print("\n Processo interrotto.")
    finally:
        conn.close()
        print("Connessione chiusa.")

if __name__ == "__main__":
    main()
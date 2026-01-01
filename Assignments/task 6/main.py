# main.py
from db_utils import get_connection
from db_loader import load_table_bulk

BATCH_SIZE = 5000  

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

    # LISTA ORDINATA TABELLE
    tables_to_load = [
        ('dim_time.csv', 'Dim_Time'),
        ('dim_artist.csv', 'Dim_Artist'),
        ('dim_album.csv', 'Dim_Album'),
        ('dim_sound.csv', 'Dim_Sound'),
        ('dim_track.csv', 'Dim_Track'), 
        ('bridge_track_artist.csv', 'Bridge_Track_Artist'),
        ('dim_youtube.csv', 'Dim_Youtube'),
        ('fact_streams.csv', 'Fact_Streams')
    ]

    try:
        for csv_file, table_name in tables_to_load:
            load_table_bulk(conn, csv_file, table_name)
        
        print(" PROCESSO COMPLETATO: DB Aggiornato!")

    except Exception as e:
        print("\n Processo interrotto.")
    finally:
        conn.close()
        print("Connessione chiusa.")

if __name__ == "__main__":
    main()

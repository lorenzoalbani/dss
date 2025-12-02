# db_loader.py
import csv
import time
import os
import pyodbc
from config import CSV_DIR, BATCH_SIZE
from db_utils import clean_row_for_sql

def load_table_bulk(conn, csv_filename, table_name):
    """
    Legge un CSV e carica i dati in SQL usando batch (blocchi).
    """
    # Combina il percorso assoluto configurato con il nome del file
    file_path = os.path.join(CSV_DIR, csv_filename)
    
    if not os.path.exists(file_path):
        print(f"⚠️  File non trovato: {file_path}")
        return

    print(f"\n--- Inizio caricamento: {table_name} ---")
    start_time = time.time()
    
    cursor = conn.cursor()
    
    # encoding='utf-8-sig' gestisce il BOM se presente (comune in Excel/Windows)
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        
        # 1. Lettura Header
        try:
            header = next(reader)
        except StopIteration:
            print(f"   [!] Il file {csv_filename} è vuoto.")
            return

        # Costruzione Query
        # Assumiamo che le colonne nel CSV abbiano lo stesso nome (o ordine) del DB
        # Se i nomi header CSV sono diversi dalle colonne DB, togli la parte ({columns})
        # e affidati solo all'ordine dei VALUES.
        columns = ", ".join(header) 
        placeholders = ", ".join(["?"] * len(header))
        
        # Query generica: INSERT INTO Tabella (Col1, Col2) VALUES (?, ?)
        sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # 2. Loop di caricamento a blocchi
        batch = []
        total_rows = 0
        
        try:
            # Disabilitiamo autocommit per velocità
            original_autocommit = conn.autocommit
            conn.autocommit = False 
            
            for row in reader:
                cleaned_row = clean_row_for_sql(row)
                batch.append(cleaned_row)
                
                # Svuota il secchio
                if len(batch) >= BATCH_SIZE:
                    cursor.executemany(sql_query, batch)
                    conn.commit()
                    total_rows += len(batch)
                    print(f"   -> Caricate {total_rows} righe...", end='\r')
                    batch = [] 
            
            # 3. Residuo finale
            if batch:
                cursor.executemany(sql_query, batch)
                conn.commit()
                total_rows += len(batch)
                
            print(f"\n✅ Completato {table_name}: {total_rows} righe in {round(time.time() - start_time, 2)}s.")
            
        except pyodbc.Error as e:
            conn.rollback()
            print(f"\n❌ ERRORE CRITICO SQL su {table_name}:")
            print(f"   Messaggio: {e}")
            raise 
        finally:
            conn.autocommit = original_autocommit
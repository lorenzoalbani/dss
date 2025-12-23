# db_loader.py
import csv
import time
import os
import pyodbc
from config import CSV_DIR, BATCH_SIZE
from db_utils import clean_row_for_sql

def load_table_bulk(conn, csv_filename, table_name):
    file_path = os.path.join(CSV_DIR, csv_filename)
    
    if not os.path.exists(file_path):
        print(f"File {csv_filename} non trovato in {CSV_DIR}. Salto.")
        return

    print(f"\n Inizio caricamento: {table_name}")
    start_time = time.time()
    
    cursor = conn.cursor()
    
    # Forziamo SQL a leggere le date come Anno-Mese-Giorno
    cursor.execute("SET DATEFORMAT ymd;") 
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
        
        try:
            header = next(reader)
        except StopIteration:
            return

        columns = ", ".join(header)
        placeholders = ", ".join(["?"] * len(header))
        
        sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        batch = []
        total_rows = 0
        
        try:
            original_autocommit = conn.autocommit
            conn.autocommit = False 
            
            for row in reader:
                # Qui viene chiamata la nuova funzione che corregge le date -00-
                cleaned_row = clean_row_for_sql(row)
                batch.append(cleaned_row)
                
                if len(batch) >= BATCH_SIZE:
                    cursor.executemany(sql_query, batch)
                    conn.commit()
                    total_rows += len(batch)
                    print(f" Caricate {total_rows} righe...", end='\r')
                    batch = [] 
            
            if batch:
                cursor.executemany(sql_query, batch)
                conn.commit()
                total_rows += len(batch)
                
            print(f"\nCompletato {table_name}: {total_rows} righe in {round(time.time() - start_time, 2)}s.")
            
        except pyodbc.Error as e:
            conn.rollback() 
            print(f"\nERRORE CRITICO SQL su {table_name}:")
            print(f"   Messaggio: {e}")
            raise 
        finally:
            conn.autocommit = original_autocommit

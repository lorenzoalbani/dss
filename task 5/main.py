# main.py
from etl_processor import generate_dw_files
import os

# Configurazione Percorsi
INPUT_JSON = 'track_mood_noduplicati_refactoringids.json'
INPUT_XML = 'artists.xml'

# Controllo esistenza file
if not os.path.exists(INPUT_JSON):
    print(f"Errore: File {INPUT_JSON} non trovato.")
    exit()

if __name__ == "__main__":
    try:
        generate_dw_files(INPUT_JSON, INPUT_XML)
        print("Tutto completato! I file CSV sono pronti.")
    except Exception as e:
        print(f"Si è verificato un errore critico: {e}")
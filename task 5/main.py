from etl_processor import generate_dw_files

# Assicurati che il nome del JSON sia esatto
# Se è nella Task 5, devi mettere "../task 5/track_mood_noduplicati_refactoringids.json"
JSON_FILE = "track_mood_noduplicati_refactoringids.json" 
XML_FILE = "artists.xml"

if __name__ == "__main__":
    generate_dw_files(JSON_FILE, XML_FILE)
from etl_processor import generate_dw_files

# Assicurarsi che il nome del JSON sia esatto
JSON_FILE = "tracks_moods.json" 
XML_FILE = "artists_filled.xml"

if __name__ == "__main__":
    generate_dw_files(JSON_FILE, XML_FILE)

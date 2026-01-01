from utils import (
    load_json, save_json, remove_duplicates,
    assign_track_ids, assign_album_ids
)

INPUT_FILE = 'tracks.json'
DUPES_FILE = 'tracks_noduplicati.json'
TRACKS_FILE = 'tracks_noduplicati_idt.json'
FINAL_FILE = 'tracks_preprocessingdone.json'

def main():
    # parte 1: Rimuovo i duplicati
    data = load_json(INPUT_FILE)
    data = remove_duplicates(data)
    save_json(data, DUPES_FILE)
    
    # parte 2: riassegno gli ID alle tracce
    data = assign_track_ids(data)
    save_json(data, TRACKS_FILE)
    
    # parte 3: riassegno gli ID agli album
    data = assign_album_ids(data)
    save_json(data, FINAL_FILE)

if __name__ == '__main__':
    main()

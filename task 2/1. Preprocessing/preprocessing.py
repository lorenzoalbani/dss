from utils import (
    load_json, save_json, remove_duplicates,
    assign_track_ids, assign_album_ids
)

INPUT_FILE = 'tracks.json'
DUPES_FILE = 'tracks_noduplicati.json'
TRACKS_FILE = 'tracks_noduplicati_idt.json'
FINAL_FILE = 'tracks_preprocessingdone.json'

def main():
    # Step 1: Rimuovi duplicati
    data = load_json(INPUT_FILE)
    data = remove_duplicates(data)
    save_json(data, DUPES_FILE)
    
    # Step 2: Assegna ID tracce
    data = assign_track_ids(data)
    save_json(data, TRACKS_FILE)
    
    # Step 3: Assegna ID album
    data = assign_album_ids(data)
    save_json(data, FINAL_FILE)

if __name__ == '__main__':
    main()

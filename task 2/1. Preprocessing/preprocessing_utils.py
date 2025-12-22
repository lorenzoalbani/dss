import json

def load_json(file_path):
    """Carica dati JSON da file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path, indent=2):
    """Salva dati JSON in file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)

def remove_duplicates(data):
    """Rimuove duplicati basati su title e primary_artist."""
    seen = set()
    cleaned_data = []
    for item in data:
        key = (item['title'], item['primary_artist'])
        if key not in seen:
            seen.add(key)
            cleaned_data.append(item)
    print(f"Originale: {len(data)}, Finale: {len(cleaned_data)}")
    return cleaned_data

def assign_track_ids(data):
    """Assegna ID univoci 'TRxxxxxx' alle tracce."""
    for idx, item in enumerate(data, start=1):
        item['id'] = f'TR{str(idx).zfill(6)}'
    return data

def assign_album_ids(data):
    """Assegna ID univoci 'ALxxxxxx' agli album."""
    album_to_id = {}
    next_id = 1
    for item in data:
        album = item['album']
        if album not in album_to_id:
            album_to_id[album] = f'AL{str(next_id).zfill(6)}'
            next_id += 1
        item['id_album'] = album_to_id[album]
    return data

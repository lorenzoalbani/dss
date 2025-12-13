import json
import csv
from youtube_utils import get_virality_tier

# CONFIGURAZIONE FILE
file_json_tracks = 'tracks.json'  # Il tuo file JSON delle tracce
file_csv_youtube = 'songs_with_youtube_stats.csv'             # Il tuo file CSV di YouTube
file_output      = 'tracks_with_yt.json'  # Il file finale da dare a SSIS

# Carica le Tracce (JSON)
with open(file_json_tracks, 'r', encoding='utf-8') as f_json:
    tracks_list = json.load(f_json)

# Carica i dati YouTube (CSV)
youtube_list = []
with open(file_csv_youtube, 'r', encoding='utf-8') as f_csv:

    reader = csv.DictReader(f_csv, delimiter=',') 
    for row in reader:
        youtube_list.append(row)

# Controllo di Sicurezza (Lunghezze)
len_tracks = len(tracks_list)
len_yt = len(youtube_list)

print(f"📊 Righe Tracks: {len_tracks}")
print(f"📊 Righe YouTube: {len_yt}")

if len_tracks != len_yt:
    print("Le lunghezze non coincidono!")

# Unione e Generazione Nuovo ID
merged_data = []

print("🔄 Avvio unione e rigenerazione ID...")

# Zip accoppia il 1° elemento col 1°, il 2° col 2°, ecc.
# Enumerate serve per creare il nuovo ID (1, 2, 3...)
for idx, (track, yt_row) in enumerate(zip(tracks_list, youtube_list), start=1):
    
    # A. Crea l'oggetto unito (copia i dati della traccia)
    merged_item = track.copy()
    
    # Recupero i valori grezzi
    raw_views = yt_row.get('yt_view_count')

    # colonne di interesse
    # merged_item['yt_views']      = raw_views
    # merged_item['yt_likes']      = yt_row.get('yt_like_count')
    # merged_item['yt_comment']   = yt_row.get('yt_comment_count')
    
    merged_item['yt_virality'] = get_virality_tier(raw_views)

    # SOLUZIONE DUPLICATI
    new_unique_id = f"TR{str(idx).zfill(6)}"
    
    merged_item['original_id_bugged'] = track.get('id')
    merged_item['id'] = new_unique_id

    merged_data.append(merged_item)

# Salvataggio
with open(file_output, 'w', encoding='utf-8') as f_out:
    json.dump(merged_data, f_out, indent=2)

print(f"File salvato come: {file_output}")
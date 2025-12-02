import json
import csv
import xml.etree.ElementTree as ET
import os
from datetime import datetime

# --- FUNZIONI DI UTILITÀ INTEGRATE (Per evitare problemi di import) ---
def clean_date(date_str):
    """Pulisce e valida rigorosamente le date per SQL Server."""
    if not date_str: return None
    s = str(date_str).strip()
    if not s: return None
    
    # Caso anno singolo "1990" -> "1990-01-01"
    if len(s) == 4 and s.isdigit():
        return f"{s}-01-01"
    
    s = s.replace("-00", "-01") # Fix mesi/giorni zero
    
    try:
        datetime.strptime(s, "%Y-%m-%d") # Verifica validità calendario
        return s
    except ValueError:
        return None # Data non valida (es. 30 Febbraio)

def clean_text(text):
    """Rimuove newline e caratteri strani per evitare di rompere il CSV."""
    if text is None: return ""
    return str(text).replace('\n', ' ').replace('\r', '').strip()

def safe_int(value):
    try: return int(float(value))
    except (ValueError, TypeError): return 0

def safe_float(value):
    if value is None: return 0.0
    try: return float(value)
    except (ValueError, TypeError): return 0.0

def get_season(month):
    if month in [12, 1, 2]: return 'Inverno'
    elif month in [3, 4, 5]: return 'Primavera'
    elif month in [6, 7, 8]: return 'Estate'
    else: return 'Autunno'

def get_quarter(month):
    return (month - 1) // 3 + 1

# --- FUNZIONE GENERATORE PRINCIPALE ---
def generate_dw_files(json_path, xml_path):
    print("=== INIZIO GENERAZIONE CSV ===")
    
    # 1. SETUP CARTELLE
    # Salviamo i CSV in una cartella 'csv_db' proprio qui vicino allo script
    output_dir = 'csv_db' 
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"-> Creata cartella: {output_dir}")

    # 2. CARICAMENTO ARTISTI (XML)
    print("-> Caricamento Artisti da XML...")
    artists_db = {}
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"ERRORE LETTURA XML: {e}")
        return

    def get_xml_text(row_element, tag_name):
        el = row_element.find(tag_name)
        return el.text if el is not None else None

    for row in root.findall('row'):
        a_id = get_xml_text(row, 'id_author')
        if not a_id: continue
        
        artists_db[a_id] = {
            'id': a_id,
            'name': get_xml_text(row, 'name'),
            'gender': get_xml_text(row, 'gender'),
            'birth_date': clean_date(get_xml_text(row, 'birth_date')),
            'birth_place': get_xml_text(row, 'birth_place'),
            'nationality': get_xml_text(row, 'nationality'),
            'description': clean_text(get_xml_text(row, 'description')),
            'country': get_xml_text(row, 'country'),
            'region': get_xml_text(row, 'region'),
            'province': get_xml_text(row, 'province'),
            'latitude': safe_float(get_xml_text(row, 'latitude')),
            'longitude': safe_float(get_xml_text(row, 'longitude')),
            'active_start': clean_date(get_xml_text(row, 'active_start')),
            'active_end': clean_date(get_xml_text(row, 'active_end'))
        }

    # 3. CARICAMENTO TRACCE (JSON)
    print(f"-> Caricamento JSON da: {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERRORE LETTURA JSON: {e}")
        return

    # 4. AGGIORNAMENTO NOMI ARTISTI (Primary)
    print("-> Normalizzazione nomi Primary Artist...")
    for row in data:
        p_id = row.get('id_artist')
        p_name = row.get('primary_artist')
        if p_id and p_name:
            if p_id in artists_db:
                artists_db[p_id]['name'] = p_name
            else:
                # Crea placeholder per artista mancante nell'XML
                artists_db[p_id] = {
                    'id': p_id, 'name': p_name, 'gender': 'Unknown', 'birth_date': None, 
                    'birth_place': None, 'nationality': None, 'description': 'From JSON Primary', 
                    'country': None, 'region': None, 'province': None, 
                    'latitude': 0.0, 'longitude': 0.0, 'active_start': None, 'active_end': None
                }

    # Mappa NOME -> ID per lookup veloce
    name_to_id_map = {data['name'].strip().lower(): aid for aid, data in artists_db.items() if data['name']}

    # 5. SCRITTURA FILE CSV
    print("-> Scrittura file CSV in corso...")

    # Dizionario file handles e writers
    files = {}
    writers = {}
    
    file_names = {
        'dim_time': 'dim_time.csv', 
        'dim_album': 'dim_album.csv', 
        'dim_sound': 'dim_sound.csv',
        'dim_track': 'dim_track.csv', 
        'bridge': 'bridge_track_artist.csv', 
        'fact': 'fact_streams.csv'
    }

    # Apertura di tutti i file
    for key, fname in file_names.items():
        f_path = os.path.join(output_dir, fname)
        f = open(f_path, 'w', newline='', encoding='utf-8')
        files[key] = f
        writers[key] = csv.writer(f)

    # Scrittura Headers
    writers['dim_time'].writerow(['date_id', 'full_date', 'year', 'month', 'day', 'quarter', 'season'])
    writers['dim_album'].writerow(['album_id', 'title', 'release_date', 'album_type'])
    writers['dim_sound'].writerow(['sound_id', 'bpm', 'rolloff', 'flux', 'rms', 'flatness', 'spectral_complexity', 'pitch', 'loudness', 'mood'])
    writers['dim_track'].writerow(['track_id', 'title', 'language', 'explicit', 'disc_number', 'track_number', 'duration_ms', 'swear_it', 'swear_en', 'n_sentences', 'n_tokens', 'char_per_tok', 'avg_token_per_clause', 'swear_it_words', 'swear_en_words', 'lyrics'])
    writers['bridge'].writerow(['track_id', 'artist_id', 'role'])
    writers['fact'].writerow(['track_id', 'album_id', 'date_id', 'sound_id', 'main_artist_id', 'streams_1month', 'popularity'])

    # Cache per duplicati
    seen_time = set()
    seen_albums = set()
    seen_tracks = set()
    
    sound_counter = 1
    new_artist_counter = 1
    processed_count = 0

    # LOOP PRINCIPALE
    for row in data:
        track_id = row.get('id')
        if not track_id: continue

        # Evita duplicati canzone
        if track_id in seen_tracks: continue
        seen_tracks.add(track_id)
        
        processed_count += 1

        # --- BRIDGE (Artisti) ---
        main_id = row.get('id_artist')
        if main_id:
            writers['bridge'].writerow([track_id, main_id, 'Main'])

        feat_str = row.get('featured_artists')
        if feat_str:
            feats = [x.strip() for x in feat_str.split(',')]
            for f_name in feats:
                if not f_name: continue
                f_key = f_name.lower()
                
                if f_key in name_to_id_map:
                    final_id = name_to_id_map[f_key]
                else:
                    final_id = f"ART_NEW_{new_artist_counter:04d}"
                    new_artist_counter += 1
                    name_to_id_map[f_key] = final_id
                    artists_db[final_id] = {
                        'id': final_id, 'name': f_name, 'gender': 'Unknown', 'birth_date': None, 
                        'birth_place': None, 'nationality': None, 'description': 'Auto-generated', 
                        'country': None, 'region': None, 'province': None, 
                        'latitude': 0.0, 'longitude': 0.0, 'active_start': None, 'active_end': None
                    }
                writers['bridge'].writerow([track_id, final_id, 'Featured'])

        # --- DIM TIME ---
        y, m, d = safe_int(row.get('year')), safe_int(row.get('month')), safe_int(row.get('day'))
        # Fix date nulle o zero
        if y == 0 or m == 0 or d == 0:
            date_id = 19000101
            full_date = "1900-01-01"
            y, m, d = 1900, 1, 1
        else:
            date_id = y * 10000 + m * 100 + d
            full_date = f"{y}-{m:02d}-{d:02d}"

        if date_id not in seen_time:
            writers['dim_time'].writerow([date_id, full_date, y, m, d, get_quarter(m), get_season(m)])
            seen_time.add(date_id)

        # --- DIM ALBUM ---
        alb_id = row.get('id_album')
        if alb_id and alb_id not in seen_albums:
            clean_rel = clean_date(row.get('album_release_date'))
            writers['dim_album'].writerow([alb_id, row.get('album_name'), clean_rel, row.get('album_type')])
            seen_albums.add(alb_id)

        # --- DIM SOUND ---
        curr_sound_id = sound_counter
        writers['dim_sound'].writerow([
            curr_sound_id, safe_float(row.get('bpm')), safe_float(row.get('rolloff')), 
            safe_float(row.get('flux')), safe_float(row.get('rms')), safe_float(row.get('flatness')), 
            safe_float(row.get('spectral_complexity')), safe_float(row.get('pitch')), 
            safe_float(row.get('loudness')), row.get('mood', 'Unknown')
        ])
        sound_counter += 1

        # --- DIM TRACK ---
        writers['dim_track'].writerow([
            track_id, row.get('title'), row.get('language'), 
            1 if row.get('explicit') else 0, safe_int(row.get('disc_number')), 
            safe_int(row.get('track_number')), safe_float(row.get('duration_ms')), 
            safe_int(row.get('swear_IT')), safe_int(row.get('swear_EN')), 
            safe_float(row.get('n_sentences')), safe_float(row.get('n_tokens')), 
            safe_float(row.get('char_per_tok')), safe_float(row.get('avg_token_per_clause')), 
            str(row.get('swear_IT_words', [])), str(row.get('swear_EN_words', [])), 
            clean_text(row.get('lyrics'))
        ])

        # --- FACT ---
        writers['fact'].writerow([
            track_id, alb_id, date_id, curr_sound_id, main_id, 
            safe_int(row.get('streams@1month')), safe_float(row.get('popularity'))
        ])

    # Chiusura file Loop
    for f in files.values():
        f.close()
    
    print(f"-> Processate {processed_count} tracce.")

    # 6. SCRITTURA FINALE DIM_ARTIST
    print(f"-> Scrittura finale {len(artists_db)} artisti...")
    
    path_artist = os.path.join(output_dir, 'dim_artist.csv')
    with open(path_artist, 'w', newline='', encoding='utf-8') as f_art:
        w_art = csv.writer(f_art)
        w_art.writerow(['artist_id', 'name', 'gender', 'birth_date', 'birth_place', 
                        'nationality', 'description', 'country', 'region', 
                        'province', 'latitude', 'longitude', 'active_start', 'active_end'])
        
        for aid, data in artists_db.items():
            w_art.writerow([
                data['id'], data['name'], data['gender'], data['birth_date'], 
                data['birth_place'], data['nationality'], data['description'], 
                data['country'], data['region'], data['province'], 
                data['latitude'], data['longitude'], data['active_start'], data['active_end']
            ])

    print(f"=== COMPLETATO ===\nI file si trovano in: {os.path.abspath(output_dir)}")
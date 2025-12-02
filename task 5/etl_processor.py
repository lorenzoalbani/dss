# etl_processor.py
import json
import csv
import xml.etree.ElementTree as ET
from utils import safe_int, safe_float, clean_text, get_season, get_quarter
import os

def generate_dw_files(json_path, xml_path):
    print("1. Inizializzazione e creazione cartelle...")
    
    output_dir = 'csv_db'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- FASE 1: Caricamento Artisti in MEMORIA (da XML) ---
    print("2. Caricamento Artisti da XML in memoria...")
    
    # Struttura dati: Dizionario per ID -> Dati Artista
    # Esempio: artists_db['ART123'] = {'name': 'Ernia', 'gender': 'M', ...}
    artists_db = {}
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
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
            'birth_date': get_xml_text(row, 'birth_date'),
            'birth_place': get_xml_text(row, 'birth_place'),
            'nationality': get_xml_text(row, 'nationality'),
            'description': clean_text(get_xml_text(row, 'description')),
            'country': get_xml_text(row, 'country'),
            'region': get_xml_text(row, 'region'),
            'province': get_xml_text(row, 'province'),
            'latitude': safe_float(get_xml_text(row, 'latitude')),
            'longitude': safe_float(get_xml_text(row, 'longitude')),
            'active_start': get_xml_text(row, 'active_start'),
            'active_end': get_xml_text(row, 'active_end')
        }

    # Carichiamo il JSON
    print("3. Caricamento JSON...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- FASE 2: Aggiornamento Nomi Primary Artist (La tua richiesta) ---
    print("4. Normalizzazione nomi Primary Artist...")
    
    for row in data:
        p_id = row.get('id_artist')      # ID dal JSON
        p_name = row.get('primary_artist') # Nome dal JSON
        
        if p_id and p_name:
            # Se l'artista esiste nell'XML, sovrascriviamo il nome con quello del JSON
            if p_id in artists_db:
                artists_db[p_id]['name'] = p_name
            else:
                # Caso limite: L'ID del primary artist è nel JSON ma NON nell'XML
                # Lo creiamo ora per evitare errori di Foreign Key dopo
                artists_db[p_id] = {
                    'id': p_id,
                    'name': p_name,
                    'gender': 'Unknown', 'birth_date': None, 'birth_place': None,
                    'nationality': None, 'description': 'From JSON Primary',
                    'country': None, 'region': None, 'province': None,
                    'latitude': 0.0, 'longitude': 0.0,
                    'active_start': None, 'active_end': None
                }

    # --- Creazione mappa inversa NOME -> ID aggiornata ---
    # Serve per trovare velocemente i featured artist
    name_to_id_map = {}
    for aid, data_dict in artists_db.items():
        if data_dict['name']:
            # Usiamo lower() per match case-insensitive
            name_to_id_map[data_dict['name'].strip().lower()] = aid

    # --- FASE 3: ETL e Scrittura File (Tranne Dim_Artist che scriviamo alla fine) ---
    print("5. Generazione Tabelle Fact e Dimensioni...")

    # Apertura file
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

    for key, fname in file_names.items():
        full_path = os.path.join(output_dir, fname)
        f = open(full_path, 'w', newline='', encoding='utf-8')
        files[key] = f
        writers[key] = csv.writer(f)

    # Scrittura Headers (Identici a prima)
    writers['dim_time'].writerow(['date_id', 'full_date', 'year', 'month', 'day', 'quarter', 'season'])
    writers['dim_album'].writerow(['album_id', 'title', 'release_date', 'album_type'])
    writers['dim_sound'].writerow(['sound_id', 'bpm', 'rolloff', 'flux', 'rms', 'flatness', 'spectral_complexity', 'pitch', 'loudness', 'mood'])
    writers['dim_track'].writerow(['track_id', 'title', 'language', 'explicit', 'disc_number', 'track_number', 'duration_ms', 'swear_it', 'swear_en', 'n_sentences', 'n_tokens', 'char_per_tok', 'avg_token_per_clause', 'swear_it_words', 'swear_en_words', 'lyrics'])
    writers['bridge'].writerow(['track_id', 'artist_id', 'role'])
    writers['fact'].writerow(['track_id', 'album_id', 'date_id', 'sound_id', 'main_artist_id', 'streams_1month', 'popularity'])

    # Variabili di supporto
    seen_time = set()
    seen_albums = set()
    sound_counter = 1
    new_artist_counter = 1

    for row in data:
        track_id = row.get('id')
        if not track_id: continue

        # --- GESTIONE ARTISTI (BRIDGE) ---
        
        # 1. Main Artist
        main_id = row.get('id_artist')
        if main_id:
            writers['bridge'].writerow([track_id, main_id, 'Main'])

        # 2. Featured Artists
        feat_str = row.get('featured_artists')
        if feat_str:
            feats = [x.strip() for x in feat_str.split(',')]
            for f_name in feats:
                if not f_name: continue
                
                f_key = f_name.lower()
                
                # Cerchiamo nella mappa aggiornata
                if f_key in name_to_id_map:
                    final_id = name_to_id_map[f_key]
                else:
                    # NUOVO ARTISTA FEATURED TROVATO
                    final_id = f"ART_NEW_{new_artist_counter:04d}"
                    new_artist_counter += 1
                    
                    # 1. Aggiorniamo la mappa
                    name_to_id_map[f_key] = final_id
                    
                    # 2. Aggiungiamo al DB in memoria (verrà scritto alla fine nel CSV)
                    artists_db[final_id] = {
                        'id': final_id,
                        'name': f_name, # Usiamo il nome originale (col casing corretto)
                        'gender': 'Unknown', 'birth_date': None, 'birth_place': None,
                        'nationality': None, 'description': 'Auto-generated from featured',
                        'country': None, 'region': None, 'province': None,
                        'latitude': 0.0, 'longitude': 0.0,
                        'active_start': None, 'active_end': None
                    }
                
                writers['bridge'].writerow([track_id, final_id, 'Featured'])

        # --- ALTRE TABELLE (Codice Standard) ---
        # Dim Time
        y, m, d = safe_int(row.get('year')), safe_int(row.get('month')), safe_int(row.get('day'))
        date_id = y * 10000 + m * 100 + d
        if date_id not in seen_time and date_id != 0:
            full_date = f"{y}-{m:02d}-{d:02d}"
            writers['dim_time'].writerow([date_id, full_date, y, m, d, get_quarter(m), get_season(m)])
            seen_time.add(date_id)

        # Dim Album
        alb_id = row.get('id_album')
        if alb_id and alb_id not in seen_albums:
            writers['dim_album'].writerow([alb_id, row.get('album_name'), row.get('album_release_date'), row.get('album_type')])
            seen_albums.add(alb_id)

        # Dim Sound
        curr_sound_id = sound_counter
        writers['dim_sound'].writerow([
            curr_sound_id, safe_float(row.get('bpm')), safe_float(row.get('rolloff')), 
            safe_float(row.get('flux')), safe_float(row.get('rms')), safe_float(row.get('flatness')), 
            safe_float(row.get('spectral_complexity')), safe_float(row.get('pitch')), 
            safe_float(row.get('loudness')), row.get('mood', 'Unknown')
        ])
        sound_counter += 1

        # Dim Track
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

        # Fact Streams
        writers['fact'].writerow([
            track_id, alb_id, date_id, curr_sound_id, main_id, 
            safe_int(row.get('streams@1month')), safe_float(row.get('popularity'))
        ])

    # Chiudiamo i file Fact/Dim secondarie
    for f in files.values():
        f.close()

    # --- FASE 4: Scrittura Finale DIM_ARTIST ---
    print(f"6. Scrittura finale {len(artists_db)} artisti in CSV...")
    
    path_artist = os.path.join(output_dir, 'dim_artist.csv')
    with open(path_artist, 'w', newline='', encoding='utf-8') as f_art:
        w_art = csv.writer(f_art)
        
        # Header
        w_art.writerow(['artist_id', 'name', 'gender', 'birth_date', 'birth_place', 
                        'nationality', 'description', 'country', 'region', 
                        'province', 'latitude', 'longitude', 'active_start', 'active_end'])
        
        # Scriviamo tutti gli artisti dal dizionario (che ora include XML + Aggiornamenti JSON + Nuovi Featured)
        for aid, data in artists_db.items():
            w_art.writerow([
                data['id'], data['name'], data['gender'], data['birth_date'], 
                data['birth_place'], data['nationality'], data['description'], 
                data['country'], data['region'], data['province'], 
                data['latitude'], data['longitude'], data['active_start'], data['active_end']
            ])

    print(f"Generazione Completata. File salvati in: {output_dir}/")
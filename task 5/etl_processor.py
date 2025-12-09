import json
import csv
import xml.etree.ElementTree as ET
import os
import unicodedata
# Assicurati che utils.py sia nella stessa cartella
from utils import clean_text, safe_int, safe_float, get_season, get_quarter

# --- FUNZIONI DI SUPPORTO LOCALI ---

def clean_date(date_str):
    """Pulisce le date per formato SQL YYYY-MM-DD"""
    if not date_str: return None
    d = str(date_str).strip()
    if not d: return None
    if len(d) == 4 and d.isdigit(): return f"{d}-01-01"
    if "-00" in d: d = d.replace("-00", "-01")
    if len(d) < 8: return None
    return d

def normalize(name):
    """
    Normalizzazione aggressiva per matching nomi.
    Es: "Guè Pequeno" -> "gue pequeno"
    """
    if not name: return None
    # 1. Unifica apostrofi e rimuove punteggiatura
    name = name.replace("’", "'").replace("‘", "'").replace("`", "'")
    name = name.replace(".", " ").replace("-", " ")
    # 2. Rimuove accenti (Unicode Normalization)
    name = unicodedata.normalize('NFKD', name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    # 3. Lowercase e strip
    return ' '.join(name.split()).lower()

def get_xml_text(row_element, tag_name):
    el = row_element.find(tag_name)
    return el.text if el is not None else None

# --- FUNZIONE PRINCIPALE ---

def generate_dw_files(json_path, xml_path):
    print("=== INIZIO GENERAZIONE DATA WAREHOUSE (V. DEFINITIVA) ===")
    
    output_dir = 'csv_db'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- STRUTTURE DATI ---
    # Mappa: Nome Normalizzato -> ID Numerico DW
    name_to_dw_id = {} 
    # Mappa: ID Originale XML (es. 'A1') -> ID Numerico DW (es. 10)
    xml_id_to_dw_id = {}
    # Registro finale per dim_artist.csv
    final_artists_registry = {}

    artist_counter = 1

    # --- FASE 1: CARICAMENTO BASE DA XML ---
    print("1. Indicizzazione artisti da XML...")
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        for row in root.findall('row'):
            old_xml_id = get_xml_text(row, 'id_author')
            raw_name = get_xml_text(row, 'name')
            
            if not raw_name: continue

            norm_name = normalize(raw_name)
            current_dw_id = artist_counter
            artist_counter += 1

            # Mappature
            if old_xml_id:
                xml_id_to_dw_id[old_xml_id] = current_dw_id
            if norm_name:
                name_to_dw_id[norm_name] = current_dw_id

            # Salvataggio dati completi
            final_artists_registry[current_dw_id] = {
                'artist_id': current_dw_id,
                'name': raw_name,
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
                'active_end': clean_date(get_xml_text(row, 'active_end')),
                'source': 'XML'
            }
    except Exception as e:
        print(f"Errore lettura XML: {e}")
        return

    # --- FASE 2: APPRENDIMENTO ALIAS DA JSON ---
    print("2. Scansione JSON per alias...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    aliases_count = 0
    for row in data:
        # Se ID JSON corrisponde a ID XML, mappiamo il nome JSON all'ID esistente
        j_id = row.get('id_artist')
        j_name = row.get('primary_artist')
        
        if j_id and j_name and j_id in xml_id_to_dw_id:
            real_id = xml_id_to_dw_id[j_id]
            norm_j_name = normalize(j_name)
            
            if norm_j_name and norm_j_name not in name_to_dw_id:
                name_to_dw_id[norm_j_name] = real_id
                aliases_count += 1
    
    print(f"   Alias appresi: {aliases_count}")

    # --- FASE 3: PREPARAZIONE FILE CSV ---
    files = {}
    writers = {}
    file_names = {
        'dim_time': 'dim_time.csv', 'dim_album': 'dim_album.csv', 
        'dim_sound': 'dim_sound.csv', 'dim_track': 'dim_track.csv',
        'dim_artist': 'dim_artist.csv', 'bridge': 'bridge_track_artist.csv',
        'fact': 'fact_streams.csv'
    }

    for key, fname in file_names.items():
        f = open(os.path.join(output_dir, fname), 'w', newline='', encoding='utf-8')
        files[key] = f
        writers[key] = csv.writer(f)

    # Scrittura Headers
    writers['dim_time'].writerow(['date_id', 'full_date', 'year', 'month', 'day', 'quarter', 'season'])
    writers['dim_album'].writerow(['album_id', 'title', 'release_date', 'album_type'])
    writers['dim_sound'].writerow(['sound_id', 'bpm', 'rolloff', 'flux', 'rms', 'flatness', 'spectral_complexity', 'pitch', 'loudness', 'mood'])
    writers['dim_track'].writerow(['track_id', 'title', 'language', 'explicit', 'disc_number', 'track_number', 'duration_ms', 'swear_it', 'swear_en', 'n_sentences', 'n_tokens', 'char_per_tok', 'avg_token_per_clause', 'swear_it_words', 'swear_en_words', 'lyrics'])
    writers['dim_artist'].writerow(['artist_id', 'name', 'gender', 'birth_date', 'birth_place', 'nationality', 'description', 'country', 'region', 'province', 'latitude', 'longitude', 'active_start', 'active_end'])
    writers['bridge'].writerow(['track_id', 'artist_id', 'role'])
    writers['fact'].writerow(['track_id', 'album_id', 'date_id', 'sound_id', 'main_artist_id', 'streams_1month', 'popularity'])

    # --- FIX FOREIGN KEY: INIZIALIZZAZIONE ID 0 PER DIM_TIME ---
    # Fondamentale per evitare l'errore SQL quando mancano date
    writers['dim_time'].writerow([0, '1900-01-01', 0, 0, 0, 0, 'Unknown'])
    seen_time = {0} # Set inizializzato con 0
    
    seen_albums = set()
    sound_counter = 1

    # --- FASE 4: ELABORAZIONE TRACCE ---
    print("3. Processamento tracce e scrittura...")
    
    for row in data:
        track_id = row.get('id')
        if not track_id: continue

        # --- A. GESTIONE ARTISTI ---
        
        # 1. Main Artist
        old_main_id = row.get('id_artist')
        final_main_id = None
        if old_main_id in xml_id_to_dw_id:
            final_main_id = xml_id_to_dw_id[old_main_id]
            writers['bridge'].writerow([track_id, final_main_id, 'Main'])
        
        # 2. Featured Artists
        feat_str = row.get('featured_artists')
        if feat_str:
            feats = [x.strip() for x in feat_str.split(',')]
            for f_name in feats:
                if not f_name: continue
                f_norm = normalize(f_name)
                
                # Cerca ID (XML o Alias) o Crea Nuovo
                if f_norm in name_to_dw_id:
                    f_id = name_to_dw_id[f_norm]
                else:
                    f_id = artist_counter
                    artist_counter += 1
                    name_to_dw_id[f_norm] = f_id
                    # Crea record anagrafica vuoto
                    final_artists_registry[f_id] = {
                        'artist_id': f_id,
                        'name': f_name,
                        'source': 'JSON_Featured'
                    }
                
                writers['bridge'].writerow([track_id, f_id, 'Featured'])

        # --- B. SCRITTURA DIMENSIONI ---

        # Time (Gestione 0 già fatta)
        y, m, d = safe_int(row.get('year')), safe_int(row.get('month')), safe_int(row.get('day'))
        date_id = y * 10000 + m * 100 + d
        
        if date_id not in seen_time and date_id != 0:
            safe_m = m if m > 0 else 1
            safe_d = d if d > 0 else 1
            full_date = f"{y}-{safe_m:02d}-{safe_d:02d}"
            writers['dim_time'].writerow([date_id, full_date, y, m, d, get_quarter(safe_m), get_season(safe_m)])
            seen_time.add(date_id)

        # Album
        alb_id = row.get('id_album')
        if alb_id and alb_id not in seen_albums:
            writers['dim_album'].writerow([alb_id, row.get('album_name'), clean_date(row.get('album_release_date')), row.get('album_type')])
            seen_albums.add(alb_id)

        # Sound
        curr_sound_id = sound_counter
        writers['dim_sound'].writerow([curr_sound_id, safe_float(row.get('bpm')), safe_float(row.get('rolloff')), safe_float(row.get('flux')), safe_float(row.get('rms')), safe_float(row.get('flatness')), safe_float(row.get('spectral_complexity')), safe_float(row.get('pitch')), safe_float(row.get('loudness')), row.get('mood', 'Unknown')])
        sound_counter += 1

        # Track
        writers['dim_track'].writerow([track_id, row.get('title'), row.get('language'), 1 if row.get('explicit') else 0, safe_int(row.get('disc_number')), safe_int(row.get('track_number')), safe_float(row.get('duration_ms')), safe_int(row.get('swear_IT')), safe_int(row.get('swear_EN')), safe_float(row.get('n_sentences')), safe_float(row.get('n_tokens')), safe_float(row.get('char_per_tok')), safe_float(row.get('avg_token_per_clause')), str(row.get('swear_IT_words', [])), str(row.get('swear_EN_words', [])), clean_text(row.get('lyrics'))])

        # --- C. SCRITTURA FACT TABLE ---
        writers['fact'].writerow([
            track_id, alb_id, date_id, curr_sound_id, 
            final_main_id, # ID numerico DW
            safe_int(row.get('streams@1month')), safe_float(row.get('popularity'))
        ])

    # --- FASE 5: SCRITTURA FINALE ARTISTI ---
    print(f"4. Scrittura dim_artist.csv ({len(final_artists_registry)} record)...")
    
    sorted_artists = sorted(final_artists_registry.values(), key=lambda x: x['artist_id'])
    
    for artist in sorted_artists:
        # Uso .get() per sicurezza se mancano chiavi nei featured
        writers['dim_artist'].writerow([
            artist['artist_id'],
            artist['name'],
            artist.get('gender'),
            artist.get('birth_date'),
            artist.get('birth_place'),
            artist.get('nationality'),
            artist.get('description'),
            artist.get('country'),
            artist.get('region'),
            artist.get('province'),
            artist.get('latitude'),
            artist.get('longitude'),
            artist.get('active_start'),
            artist.get('active_end')
        ])

    for f in files.values(): f.close()
    print(f"\n✅ ETL Completato! File salvati in {output_dir}/")

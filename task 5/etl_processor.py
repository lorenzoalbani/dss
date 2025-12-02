import json
import csv
import xml.etree.ElementTree as ET
import os


# --- FUNZIONI DI UTILITÀ INTEGRATE (Per evitare problemi di import) ---
def clean_date(date_str):
    """
    Pulisce e normalizza le date per SQL Server.
    Input supportati: 'YYYY-MM-DD', 'YYYY', 'YYYY-00-00', None, ''
    Output: 'YYYY-MM-DD' valido oppure None
    """
    if not date_str:
        return None
    
    d = str(date_str).strip()
    
    if not d:
        return None

    # Caso 1: Solo anno (es: "1985") -> "1985-01-01"
    if len(d) == 4 and d.isdigit():
        return f"{d}-01-01"

    # Caso 2: Date con zeri (es: "1985-00-01" o "1985-05-00")
    if "-00" in d:
        d = d.replace("-00", "-01")

    # Caso 3: Controllo lunghezza minima (YYYY-M-D sono almeno 8 char)
    if len(d) < 8:
        return None
        
    return d


def get_xml_text(row_element, tag_name):
    """Estrae il testo da un elemento XML"""
    el = row_element.find(tag_name)
    return el.text if el is not None else None


def generate_dw_files(json_path, xml_path):
    print("=== INIZIO GENERAZIONE CSV ===")
    
    output_dir = 'csv_db'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- FASE 1: Caricamento Artisti Normalizzati da XML ---
    print("2. Caricamento artisti normalizzati da XML...")
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Dizionario ID -> Dati Artista (solo lettura)
    artists_data = {}
    # Mappa nome -> ID per lookup featured artists
    name_to_id_map = {}
    
    for row in root.findall('row'):
        artist_id = get_xml_text(row, 'id_author')
        if not artist_id:
            continue
        
        artist_name = get_xml_text(row, 'name')
        
        artists_data[artist_id] = {
            'id': artist_id,
            'name': artist_name,
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
        
        # Crea mappa nome -> ID per lookup
        if artist_name:
            name_to_id_map[artist_name.strip().lower()] = artist_id
    
    print(f"   Caricati {len(artists_data)} artisti dall'XML normalizzato")

    # --- FASE 2: Caricamento JSON ---
    print("3. Caricamento JSON...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- FASE 3: Apertura File CSV ---
    print("4. Generazione Tabelle Fact e Dimensioni...")

    files = {}
    writers = {}
    
    file_names = {
        'dim_time': 'dim_time.csv', 
        'dim_album': 'dim_album.csv', 
        'dim_sound': 'dim_sound.csv',
        'dim_track': 'dim_track.csv',
        'dim_artist': 'dim_artist.csv',
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
    writers['dim_artist'].writerow(['artist_id', 'name', 'gender', 'birth_date', 'birth_place', 'nationality', 'description', 'country', 'region', 'province', 'latitude', 'longitude', 'active_start', 'active_end'])
    writers['bridge'].writerow(['track_id', 'artist_id', 'role'])
    writers['fact'].writerow(['track_id', 'album_id', 'date_id', 'sound_id', 'main_artist_id', 'streams_1month', 'popularity'])

    # Cache per duplicati
    seen_time = set()
    seen_albums = set()
    seen_tracks = set()
    
    sound_counter = 1

    # --- FASE 4: Loop Principale per Generazione CSV ---
    print("5. Processamento tracce e scrittura CSV...")
    
    for row in data:
        track_id = row.get('id')
        if not track_id:
            continue

        # --- GESTIONE BRIDGE TRACK-ARTIST ---
        
        # Main Artist
        main_id = row.get('id_artist')
        if main_id:
            writers['bridge'].writerow([track_id, main_id, 'Main'])

        # Featured Artists (lookup da mappa nome -> ID)
        feat_str = row.get('featured_artists')
        if feat_str:
            feats = [x.strip() for x in feat_str.split(',')]
            for f_name in feats:
                if not f_name:
                    continue
                
                f_key = f_name.lower()
                
                # Cerca l'ID nella mappa
                if f_key in name_to_id_map:
                    f_id = name_to_id_map[f_key]
                    writers['bridge'].writerow([track_id, f_id, 'Featured'])

        # --- DIM_TIME ---
        y = safe_int(row.get('year'))
        m = safe_int(row.get('month'))
        d = safe_int(row.get('day'))
        date_id = y * 10000 + m * 100 + d
        
        if date_id not in seen_time and date_id != 0:
            # Gestione mese/giorno = 0
            safe_m = m if m > 0 else 1
            safe_d = d if d > 0 else 1
            full_date = f"{y}-{safe_m:02d}-{safe_d:02d}"
            
            writers['dim_time'].writerow([
                date_id, 
                full_date, 
                y, 
                m, 
                d, 
                get_quarter(m if m > 0 else 1), 
                get_season(m if m > 0 else 1)
            ])
            seen_time.add(date_id)

        # --- DIM_ALBUM ---
        alb_id = row.get('id_album')
        if alb_id and alb_id not in seen_albums:
            clean_rel_date = clean_date(row.get('album_release_date'))
            writers['dim_album'].writerow([
                alb_id, 
                row.get('album_name'), 
                clean_rel_date, 
                row.get('album_type')
            ])
            seen_albums.add(alb_id)

        # --- DIM_SOUND ---
        curr_sound_id = sound_counter
        writers['dim_sound'].writerow([
            curr_sound_id, 
            safe_float(row.get('bpm')), 
            safe_float(row.get('rolloff')), 
            safe_float(row.get('flux')), 
            safe_float(row.get('rms')), 
            safe_float(row.get('flatness')), 
            safe_float(row.get('spectral_complexity')), 
            safe_float(row.get('pitch')), 
            safe_float(row.get('loudness')), 
            row.get('mood', 'Unknown')
        ])
        sound_counter += 1

        # --- DIM_TRACK ---
        writers['dim_track'].writerow([
            track_id, 
            row.get('title'), 
            row.get('language'), 
            1 if row.get('explicit') else 0, 
            safe_int(row.get('disc_number')), 
            safe_int(row.get('track_number')), 
            safe_float(row.get('duration_ms')), 
            safe_int(row.get('swear_IT')), 
            safe_int(row.get('swear_EN')), 
            safe_float(row.get('n_sentences')), 
            safe_float(row.get('n_tokens')), 
            safe_float(row.get('char_per_tok')), 
            safe_float(row.get('avg_token_per_clause')), 
            str(row.get('swear_IT_words', [])), 
            str(row.get('swear_EN_words', [])), 
            clean_text(row.get('lyrics'))
        ])

        # --- FACT_STREAMS ---
        writers['fact'].writerow([
            track_id, 
            alb_id, 
            date_id, 
            curr_sound_id, 
            main_id, 
            safe_int(row.get('streams@1month')), 
            safe_float(row.get('popularity'))
        ])

    # --- FASE 5: Scrittura DIM_ARTIST ---
    print(f"6. Scrittura {len(artists_data)} artisti in dim_artist.csv...")
    
    for artist in artists_data.values():
        writers['dim_artist'].writerow([
            artist['id'],
            artist['name'],
            artist['gender'],
            artist['birth_date'],
            artist['birth_place'],
            artist['nationality'],
            artist['description'],
            artist['country'],
            artist['region'],
            artist['province'],
            artist['latitude'],
            artist['longitude'],
            artist['active_start'],
            artist['active_end']
        ])

    # Chiusura file
    for f in files.values():
        f.close()

    print(f"\n✅ Generazione Completata! File salvati in: {output_dir}/")

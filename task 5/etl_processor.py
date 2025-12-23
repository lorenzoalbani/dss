import json
import csv
import xml.etree.ElementTree as ET
import os
import unicodedata

from utils import clean_text, safe_int, safe_float, get_season, get_quarter

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
    Normalizzazione per matching nomi.
    """
    if not name: return None
    name = name.replace("’", "'").replace("‘", "'").replace("`", "'")
    name = name.replace(".", " ").replace("-", " ")
    name = unicodedata.normalize('NFKD', name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    return ' '.join(name.split()).lower()

def get_xml_text(row_element, tag_name):
    el = row_element.find(tag_name)
    return el.text if el is not None else None

# FUNZIONE PRINCIPALE

def generate_dw_files(json_path, xml_path):
    
    output_dir = 'csv_db'
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    # --- STRUTTURE DATI ---
    name_to_dw_id = {} 
    xml_id_to_dw_id = {}
    final_artists_registry = {}
    artist_counter = 1

    # Mappa: "Global Hit" -> 1, "Niche" -> 2
    virality_map = {} 
    virality_counter = 1

    # XML
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
            if old_xml_id: xml_id_to_dw_id[old_xml_id] = current_dw_id
            if norm_name: name_to_dw_id[norm_name] = current_dw_id
            final_artists_registry[current_dw_id] = {
                'artist_id': current_dw_id, 'name': raw_name, 'gender': get_xml_text(row, 'gender'),
                'birth_date': clean_date(get_xml_text(row, 'birth_date')), 'birth_place': get_xml_text(row, 'birth_place'),
                'nationality': get_xml_text(row, 'nationality'), 'description': clean_text(get_xml_text(row, 'description')),
                'country': get_xml_text(row, 'country'), 'region': get_xml_text(row, 'region'),
                'province': get_xml_text(row, 'province'), 'latitude': safe_float(get_xml_text(row, 'latitude')),
                'longitude': safe_float(get_xml_text(row, 'longitude')), 'active_start': clean_date(get_xml_text(row, 'active_start')),
                'active_end': clean_date(get_xml_text(row, 'active_end')), 'source': 'XML'
            }
    except Exception as e:
        print(f"Errore lettura XML: {e}")
        return

    # JSON ALIAS
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for row in data:
        j_id, j_name = row.get('id_artist'), row.get('primary_artist')
        if j_id and j_name and j_id in xml_id_to_dw_id:
            real_id = xml_id_to_dw_id[j_id]
            norm_j_name = normalize(j_name)
            if norm_j_name and norm_j_name not in name_to_dw_id:
                name_to_dw_id[norm_j_name] = real_id

    # PREPARAZIONE CSV
    files = {}
    writers = {}
    # Nota: la chiamiamo sempre dim_youtube, ma concettualmente è dim_virality
    file_names = {
        'dim_time': 'dim_time.csv', 'dim_album': 'dim_album.csv', 
        'dim_sound': 'dim_sound.csv', 'dim_youtube': 'dim_youtube.csv',
        'dim_track': 'dim_track.csv', 'dim_artist': 'dim_artist.csv', 
        'bridge': 'bridge_track_artist.csv', 'fact': 'fact_streams.csv'
    }

    for key, fname in file_names.items():
        f = open(os.path.join(output_dir, fname), 'w', newline='', encoding='utf-8')
        files[key] = f
        writers[key] = csv.writer(f, quoting=csv.QUOTE_MINIMAL)

    # HEADERS
    writers['dim_time'].writerow(['date_id', 'full_date', 'year', 'month', 'day', 'quarter', 'season'])
    writers['dim_album'].writerow(['album_id', 'title', 'release_date', 'album_type'])
    writers['dim_sound'].writerow(['sound_id', 'bpm', 'rolloff', 'flux', 'rms', 'flatness', 'spectral_complexity', 'pitch', 'loudness', 'mood'])
    
    # HEADER YOUTUBE: Solo ID e Classe
    writers['dim_youtube'].writerow(['virality_id', 'virality_tier']) 

    writers['dim_track'].writerow(['track_id', 'title', 'language', 'explicit', 'disc_number', 'track_number', 'duration_ms', 'swear_it', 'swear_en', 'n_sentences', 'n_tokens', 'char_per_tok', 'avg_token_per_clause', 'swear_it_words', 'swear_en_words', 'lyrics'])
    writers['dim_artist'].writerow(['artist_id', 'name', 'gender', 'birth_date', 'birth_place', 'nationality', 'description', 'country', 'region', 'province', 'latitude', 'longitude', 'active_start', 'active_end'])
    writers['bridge'].writerow(['track_id', 'artist_id', 'role'])
    
    # FACT TABLE: Usa virality_id invece di youtube_id generico
    writers['fact'].writerow(['track_id', 'album_id', 'date_id', 'sound_id', 'virality_id', 'main_artist_id', 'streams_1month', 'popularity'])

    # Inizializzazioni
    writers['dim_time'].writerow([0, '1900-01-01', 0, 0, 0, 0, 'Unknown'])
    seen_time = {0}
    seen_albums = set()
    sound_counter = 1

    # PROCESSING
    for row in data:
        track_id = row.get('id')
        if not track_id: continue

        # ARTISTI
        old_main_id = row.get('id_artist')
        final_main_id = xml_id_to_dw_id.get(old_main_id)
        if final_main_id: writers['bridge'].writerow([track_id, final_main_id, 'Main'])
        
        # Featured
        feat_str = row.get('featured_artists')
        if feat_str:
            for f_name in [x.strip() for x in feat_str.split(',') if x.strip()]:
                f_norm = normalize(f_name)
                if f_norm in name_to_dw_id: f_id = name_to_dw_id[f_norm]
                else:
                    f_id = artist_counter; artist_counter += 1
                    name_to_dw_id[f_norm] = f_id
                    final_artists_registry[f_id] = {'artist_id': f_id, 'name': f_name, 'source': 'JSON_Featured'}
                writers['bridge'].writerow([track_id, f_id, 'Featured'])

        y, m, d = safe_int(row.get('year')), safe_int(row.get('month')), safe_int(row.get('day'))
        date_id = y * 10000 + m * 100 + d
        
        if date_id not in seen_time and date_id != 0:
            # Preparo i valori "safe"
            sql_m = m if m > 0 else 1
            sql_d = d if d > 0 else 1
            
            # Logica condizionale per Stagione e Quarter
            if m > 0:
                # Se il mese esiste, calcolo normalmente
                calc_season = get_season(m)
                calc_quarter = get_quarter(m)
            else:
                # Se il mese è 0 o mancante, forzo a Unknown
                calc_season = 'Unknown'
                calc_quarter = 0 
            
            writers['dim_time'].writerow([
                date_id, 
                f"{y}-{sql_m:02d}-{sql_d:02d}",
                y, 
                m, 
                d, 
                calc_quarter, 
                calc_season 
            ])
            seen_time.add(date_id)

        alb_id = row.get('id_album')
        if alb_id and alb_id not in seen_albums:
            writers['dim_album'].writerow([alb_id, row.get('album'), clean_date(row.get('album_release_date')), row.get('album_type')])
            seen_albums.add(alb_id)

        # SOUND
        curr_sound_id = sound_counter
        writers['dim_sound'].writerow([curr_sound_id, safe_float(row.get('bpm')), safe_float(row.get('rolloff')), safe_float(row.get('flux')), safe_float(row.get('rms')), safe_float(row.get('flatness')), safe_float(row.get('spectral_complexity')), safe_float(row.get('pitch')), safe_float(row.get('loudness')), row.get('mood', 'Unknown')])
        sound_counter += 1

        # YOUTUBE
        tier_value = row.get('yt_virality', 'Unknown')
        
        # Controllo se l'ho già censito
        if tier_value in virality_map:
            # Se esiste, recupero l'ID
            curr_virality_id = virality_map[tier_value]
        else:
            # Se è nuovo, creo un nuovo ID e scrivo subito nel CSV
            curr_virality_id = virality_counter
            virality_map[tier_value] = curr_virality_id
            
            # Scrivo la riga unica in dim_youtube
            writers['dim_youtube'].writerow([curr_virality_id, tier_value])
            
            virality_counter += 1

        # TRACK
        writers['dim_track'].writerow([track_id, row.get('title'), row.get('language'), 1 if row.get('explicit') else 0, safe_int(row.get('disc_number')), safe_int(row.get('track_number')), safe_float(row.get('duration_ms')), safe_int(row.get('swear_IT')), safe_int(row.get('swear_EN')), safe_float(row.get('n_sentences')), safe_float(row.get('n_tokens')), safe_float(row.get('char_per_tok')), safe_float(row.get('avg_token_per_clause')), str(row.get('swear_IT_words', [])), str(row.get('swear_EN_words', [])), clean_text(row.get('lyrics'))])

        # FACT TABLE
        writers['fact'].writerow([
            track_id, 
            alb_id, 
            date_id, 
            curr_sound_id, 
            curr_virality_id,
            final_main_id, 
            safe_int(row.get('streams@1month')), 
            safe_float(row.get('popularity'))
        ])

    # SCRITTURA ARTISTI
    for artist in sorted(final_artists_registry.values(), key=lambda x: x['artist_id']):
        writers['dim_artist'].writerow([artist['artist_id'], artist['name'], artist.get('gender'), artist.get('birth_date'), artist.get('birth_place'), artist.get('nationality'), artist.get('description'), artist.get('country'), artist.get('region'), artist.get('province'), artist.get('latitude'), artist.get('longitude'), artist.get('active_start'), artist.get('active_end')])

    for f in files.values(): f.close()
    
    print("ETL Completato!")
    print(f"   Classi Viralità Trovate: {len(virality_map)}")
    print(f"   (Esempio mappatura: {list(virality_map.items())[:3]})")

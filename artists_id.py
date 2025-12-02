import json
import xml.etree.ElementTree as ET
import unicodedata

# --- 1. FUNZIONI DI UTILITÀ E NORMALIZZAZIONE ---

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Errore: File {filepath} non trovato.")
        return []

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Salvato JSON: {filepath}")

def load_xml_list(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        data = []
        for child in root:
            record = {}
            for sub in child:
                # Normalizziamo le chiavi
                k = sub.tag
                if k == 'id_author': k = 'id'
                record[k] = sub.text
            
            # Preserviamo l'ID originale per il matching
            if 'id_author' not in record and 'id' in record:
                record['_orig_id'] = record['id']
            elif 'id_author' in record:
                record['_orig_id'] = record['id_author']
            
            data.append(record)
        return data, root.tag, list(root)[0].tag
    except Exception as e:
        print(f"Errore XML: {e}")
        return [], "root", "row"

def save_xml_list(filepath, data_list, root_name, row_name):
    root = ET.Element(root_name)
    for item in data_list:
        row = ET.SubElement(root, row_name)
        for k, v in item.items():
            if k.startswith('_'): continue
            if k == 'id': k = 'id_author'
            
            sub = ET.SubElement(row, k)
            sub.text = str(v) if v is not None else ""
            
    tree = ET.ElementTree(root)
    if hasattr(ET, 'indent'): ET.indent(tree, space="  ", level=0)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)
    print(f"Salvato XML: {filepath} ({len(data_list)} records)")

def normalize(name):
    """
    Normalizzazione aggressiva per massimizzare i match.
    Gestisce accenti, apostrofi diversi, punti e spazi.
    """
    if not name: return None
    
    # 1. Unifica apostrofi e rimuove punteggiatura comune
    name = name.replace("’", "'").replace("‘", "'").replace("`", "'")
    name = name.replace(".", " ").replace("-", " ")
    
    # 2. Rimuove accenti (Unicode Normalization)
    name = unicodedata.normalize('NFKD', name)
    name = "".join([c for c in name if not unicodedata.combining(c)])
    
    # 3. Lowercase e collasso spazi multipli
    return ' '.join(name.split()).lower()

# --- 2. LOGICA CORE ---

def process_data():
    print("--- INIZIO ELABORAZIONE (AUTO-LEARNING ALIAS) ---")
    
    tracks = load_json('tracks.json')
    xml_artists, root_tag, row_tag = load_xml_list('artists.xml')
    
    # --- FASE 1: INDICIZZAZIONE XML (La Verità) ---
    # Creiamo due mappe: una per ID -> Oggetto, una per Nome -> Oggetto
    
    id_to_artist_obj = {}
    name_to_artist_obj = {} # Chiave: Nome Normalizzato
    
    final_artist_list = [] # Questa sarà la lista master
    
    for art in xml_artists:
        art['_is_new'] = False
        final_artist_list.append(art)
        
        # Mappa ID (Fondamentale)
        if art.get('_orig_id'):
            id_to_artist_obj[str(art['_orig_id'])] = art
            
        # Mappa Nome (Fallback)
        if art.get('name'):
            norm = normalize(art['name'])
            if norm: name_to_artist_obj[norm] = art

    print(f"Artisti XML caricati: {len(final_artist_list)}")
    
    # --- FASE 2: APPRENDIMENTO ALIAS (Il trucco di Pandas) ---
    # Scorriamo i Primary Artists delle tracce.
    # Se troviamo un ID conosciuto associato a un nome DIVERSO da quello XML,
    # "insegniamo" al sistema che quel nome punta allo stesso artista.
    
    learned_aliases = 0
    for track in tracks:
        p_id = str(track.get('id_artist'))
        p_name = track.get('primary_artist')
        
        # Se conosciamo l'ID (quindi l'artista esiste)...
        if p_id in id_to_artist_obj and p_name:
            p_norm = normalize(p_name)
            
            # ...ma non conosciamo ancora questo nome specifico...
            if p_norm and p_norm not in name_to_artist_obj:
                # ...lo aggiungiamo alla mappa, puntando all'oggetto artista ESISTENTE!
                artist_obj = id_to_artist_obj[p_id]
                name_to_artist_obj[p_norm] = artist_obj
                learned_aliases += 1
                
    print(f"Alias appresi automaticamente dal JSON: {learned_aliases}")
    # Esempio: Ora name_to_artist_obj["anna"] punta all'oggetto di "Anna Pepe"
    
    # --- FASE 3: IDENTIFICAZIONE FEATURED MANCANTI ---
    # Ora scorriamo i featured. Grazie alla Fase 2, riconosceremo "Anna" come esistente.
    
    new_artists_found = 0
    
    for track in tracks:
        f_str = track.get('featured_artists')
        if f_str:
            f_names = [x.strip() for x in f_str.split(',')]
            for name in f_names:
                f_norm = normalize(name)
                
                # Se il nome NON è mappato (né XML originale, né Alias appreso)
                if f_norm and f_norm not in name_to_artist_obj:
                    # Creiamo un nuovo artista
                    new_art = {
                        'name': name,
                        '_is_new': True,
                        '_orig_id': None
                    }
                    
                    # Lo aggiungiamo alla lista Master
                    final_artist_list.append(new_art)
                    # Lo aggiungiamo alla mappa per non duplicarlo se ricompare
                    name_to_artist_obj[f_norm] = new_art
                    
                    new_artists_found += 1
                    
    print(f"Nuovi artisti (solo featured) aggiunti: {new_artists_found}")
    print(f"Totale Artisti Finale: {len(final_artist_list)}")
    
    # --- FASE 4: GENERAZIONE NUOVI ID ---
    # Assegniamo ARTxxxxxxxx a tutti
    
    # Mappe finali per l'aggiornamento del JSON
    old_id_to_new_id_map = {}
    name_to_new_id_map = {} # Contiene sia nomi XML, sia Alias, sia Nuovi
    
    for i, art in enumerate(final_artist_list):
        new_id = f"ART{i+1:08d}"
        art['id'] = new_id
        
        # Popoliamo mappa ID Vecchio -> Nuovo
        if art.get('_orig_id'):
            old_id_to_new_id_map[str(art['_orig_id'])] = new_id
            
    # Rigeneriamo la mappa nomi completa basata sui nuovi ID
    # Iteriamo su name_to_artist_obj che ora contiene TUTTO (XML, Alias, Nuovi)
    for norm_name, art_obj in name_to_artist_obj.items():
        if 'id' in art_obj:
            name_to_new_id_map[norm_name] = art_obj['id']

    # --- FASE 5: AGGIORNAMENTO TRACCE ---
    updated_tracks = []
    
    for track in tracks:
        t = track.copy()
        
        # A. Update Primary (Priorità ID)
        old_pid = str(t.get('id_artist'))
        if old_pid in old_id_to_new_id_map:
            t['id_artist'] = old_id_to_new_id_map[old_pid]
        else:
            # Fallback nome (raro)
            p_norm = normalize(t.get('primary_artist'))
            if p_norm in name_to_new_id_map:
                t['id_artist'] = name_to_new_id_map[p_norm]
        
        # B. Update Featured (Priorità Nome -> ID)
        f_str = t.get('featured_artists')
        if f_str:
            raw_names = [x.strip() for x in f_str.split(',')]
            new_ids_list = []
            for name in raw_names:
                n_norm = normalize(name)
                # Troviamo l'ID (che ora gestisce anche Anna -> ID Anna Pepe)
                found_id = name_to_new_id_map.get(n_norm, name) # fallback su nome orig se fallisce
                new_ids_list.append(found_id)
            
            t['featured_artists'] = ','.join(new_ids_list)
            
        updated_tracks.append(t)
        
    # --- FASE 6: SALVATAGGIO ---
    save_xml_list('new_artists_with_id.xml', final_artist_list, root_tag, row_tag)
    save_json('new_tracks_with_artists_id.json', updated_tracks)
    print("--- FINE ---")

if __name__ == "__main__":
    process_data()
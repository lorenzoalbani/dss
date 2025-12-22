import urllib.request
import urllib.parse
import json
import time
import xml.etree.ElementTree as ET
import os
import urllib.error
import socket

# Configuration
CONTACT_EMAIL = "t.maitino@studenti.unipi.it" 
HEADERS = {
    'User-Agent': f'ArtistXMLFixer/10.0 ({CONTACT_EMAIL})',
    'Accept': 'application/json'
}

# Reference list for Italian Regions
ITALIAN_REGIONS = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", 
    "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche", 
    "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana", 
    "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"
]

# Manual Data Dictionary
MANUAL_DATA = {
    "beba":             ["Torino", "Torino", "Piemonte", "Italia"],
    "dargen d_amico":   ["Milano", "Milano", "Lombardia", "Italia"],
    "doll kill":        [None, None, "Sardegna", "Italia"],
    "eva rea":          [None, None, "Sicilia", "Italia"],
    "hindaco":          ["Leonforte", "Enna", "Sicilia", "Italia"],
    "joey funboy":      [None, "Bolzano", "Trentino-Alto Adige", "Italia"],
    "mike24":           ["Avellino", "Avellino", "Campania", "Italia"],
    "miss simpatia":    ["Falconara", "Ancona", "Marche", "Italia"],
    "mistico":          ["Milano", "Milano", "Lombardia", "Italia"],
    "nesli":            ["Senigallia", "Ancona", "Marche", "Italia"],
    "priestess":        ["Locorotondo", "Bari", "Puglia", "Italia"]
}

# --- HELPER FUNCTIONS ---

def make_request_debug(url, retries=3):
    current_delay = 3 
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 400: return None
            if e.code in [503, 429]:
                time.sleep(current_delay * 2)
                continue
            return None
        except (urllib.error.URLError, socket.timeout, ConnectionResetError):
            if attempt < retries - 1:
                print(f" [!] Unstable connection. Waiting 30s...", end=" ", flush=True)
                time.sleep(30)
            else:
                return None
    return None

def update_xml_field(element, tag_name, new_value):
    if new_value is None: return
    child = element.find(tag_name)
    if child is not None:
        child.text = str(new_value)
    else:
        new_child = ET.SubElement(element, tag_name)
        new_child.text = str(new_value)
        new_child.tail = "\n"

def update_xml_field_manual(element, tag_name, new_value):
    """ Helper specifically for manual fixes where None clears the field """
    child = element.find(tag_name)
    if child is None:
        child = ET.SubElement(element, tag_name)
        child.tail = "\n"
    if new_value is None:
        child.text = None 
    else:
        child.text = str(new_value)

# --- CORE LOGIC FUNCTIONS ---

def search_best_candidate(artist_name):
    if not artist_name: return None
    base_url = "https://musicbrainz.org/ws/2/artist/"
    lucene_query = f'"{artist_name}" OR artist:{artist_name}'
    params = {'query': lucene_query, 'fmt': 'json', 'limit': 5}
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    data = make_request_debug(url)
    if not data: return None
    
    candidates = data.get('artists', [])
    if not candidates: return None
    
    best_candidate_id = None
    best_score = -1
    found_strong_band = False
    
    print(f" -> Analyzing {len(candidates)} candidates...", end=" ")
    
    for artist in candidates:
        name = artist.get('name', '')
        score = int(artist.get('score', 0))
        atype = artist.get('type', 'Unknown')
        country = artist.get('country', '')
        disambiguation = artist.get('disambiguation', '').lower()
        area_name = artist.get('area', {}).get('name', '')

        if atype == 'Group' and score > 80:
             if artist_name.lower() in name.lower():
                 found_strong_band = True
        
        if atype == 'Person':
            is_italian = False
            if country == 'IT': is_italian = True
            if 'italian' in disambiguation: is_italian = True
            if 'italy' in area_name.lower(): is_italian = True
            
            weighted_score = score
            if is_italian: weighted_score += 40 
            
            for alias in artist.get('aliases', []):
                if artist_name.lower() == alias.get('name', '').lower():
                    weighted_score += 10
                    break
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_candidate_id = artist['id']

    if best_candidate_id and best_score > 80:
        return best_candidate_id
    if found_strong_band:
        print(f"(Group/Band detected). Ignoring.", end="")
        return None
    return None

def get_artist_info(mbid):
    if not mbid: return None
    url = f"https://musicbrainz.org/ws/2/artist/{mbid}?fmt=json"
    data = make_request_debug(url)
    info = {'start_area_id': None, 'start_area_name': None, 'birth_date': None}
    if data:
        begin_area = data.get('begin-area')
        if begin_area and 'name' in begin_area:
            info['start_area_id'] = begin_area.get('id')
            info['start_area_name'] = begin_area.get('name')
        life_span = data.get('life-span', {})
        info['birth_date'] = life_span.get('begin')
        return info
    return None

def get_full_hierarchy(start_area_id, start_area_name):
    geo_data = {'birth_place': start_area_name, 'province': None, 'region': None, 'country': None}
    current_id = start_area_id
    depth = 0
    while current_id and depth < 5:
        time.sleep(1.2)
        url = f"https://musicbrainz.org/ws/2/area/{current_id}?fmt=json&inc=area-rels"
        data = make_request_debug(url)
        if not data: break
        relations = data.get('relations', [])
        found_parent = False
        for rel in relations:
            if rel.get('type') == 'part of' and rel.get('direction') == 'backward':
                parent = rel.get('area', {})
                p_name = parent.get('name')
                p_id = parent.get('id')
                p_type = parent.get('type')
                if p_type == 'Country':
                    geo_data['country'] = p_name
                    return geo_data 
                is_region_name = p_name in ITALIAN_REGIONS or any(reg == p_name for reg in ITALIAN_REGIONS)
                if is_region_name:
                    geo_data['region'] = p_name
                    if not geo_data['country']: geo_data['country'] = 'Italy'
                elif p_type in ['Subdivision', 'District', 'County', 'Municipality']:
                    if not is_region_name and not geo_data['province']: 
                        geo_data['province'] = p_name
                current_id = p_id
                found_parent = True
                depth += 1
                break 
        if not found_parent: break
    return geo_data

# --- MAIN FUNCTIONS TO CALL ---

def process_xml_dataset(input_file, output_file):
    print(f"--- Starting Automatic Processing (MusicBrainz) ---")
    print(f"Input: {input_file} | Output: {output_file}")
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return

    count_ok = 0
    count_total = 0

    for artist_element in root:
        count_total += 1
        name_node = artist_element.find('name')
        if name_node is None or not name_node.text: continue
        name = name_node.text.strip()
        
        fields_to_check = ['birth_place', 'province', 'region', 'country', 'birth_date', 'nationality']
        missing_fields = []
        for f in fields_to_check:
            node = artist_element.find(f)
            if node is None or not node.text or node.text.strip().lower() in ['nan', '']:
                missing_fields.append(f)
        
        if missing_fields:
            print(f"\n[{count_total}] {name}...", end=" ", flush=True)
            time.sleep(2.0)
            mbid = search_best_candidate(name)
            
            if mbid:
                time.sleep(1.5)
                artist_info = get_artist_info(mbid)
                if artist_info:
                    if artist_info['birth_date']:
                        print(f"✅ Date: {artist_info['birth_date']} ", end="")
                        update_xml_field(artist_element, 'birth_date', artist_info['birth_date'])
                    
                    if artist_info['start_area_id']:
                        print(f"✅ City: {artist_info['start_area_name']} -> Hierarchy...", end="")
                        full_geo = get_full_hierarchy(artist_info['start_area_id'], artist_info['start_area_name'])
                        
                        final_country = full_geo['country']
                        if final_country == 'Italy': final_country = 'Italia'
                        
                        debug_str = []
                        if full_geo['province']: debug_str.append(f"Prov:{full_geo['province']}")
                        if full_geo['region']: debug_str.append(f"Reg:{full_geo['region']}")
                        if final_country: debug_str.append(f"Country:{final_country}")
                        print(f" -> {', '.join(debug_str)}")
                        
                        update_xml_field(artist_element, 'birth_place', full_geo['birth_place'])
                        update_xml_field(artist_element, 'province', full_geo['province'])
                        update_xml_field(artist_element, 'region', full_geo['region'])
                        update_xml_field(artist_element, 'country', final_country)
                        if final_country == 'Italia':
                            update_xml_field(artist_element, 'nationality', 'Italia')
                    else:
                        print(f"⚠️  Missing location.", end="")
                    count_ok += 1
                else:
                    print(f"⚠️  Missing data.")
            else:
                pass 

    print(f"\n--- Automatic Processing Finished ---")
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"Saved intermediate file: {output_file}")

def apply_manual_fixes(target_file):
    print(f"\n--- Starting Manual Data Injection (In-Place) ---")
    print(f"Target File: {target_file}")

    if not os.path.exists(target_file):
        print(f"Error: File '{target_file}' not found.")
        return

    try:
        tree = ET.parse(target_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return

    count_updated = 0

    for artist_element in root:
        name_node = artist_element.find('name')
        if name_node is None or not name_node.text: continue
        name = name_node.text.strip().lower()

        if name in MANUAL_DATA:
            print(f" -> Applying manual patch for: {name}")
            data = MANUAL_DATA[name]
            
            update_xml_field_manual(artist_element, 'birth_place', data[0])
            update_xml_field_manual(artist_element, 'province', data[1])
            update_xml_field_manual(artist_element, 'region', data[2])
            update_xml_field_manual(artist_element, 'country', data[3])

            if data[3] == 'Italia':
                update_xml_field_manual(artist_element, 'nationality', 'Italia')
            count_updated += 1

    print(f"--- Manual Fixes Finished ---")
    tree.write(target_file, encoding='utf-8', xml_declaration=True)
    print(f"File updated successfully: {target_file}")


def main():
    original_xml = "artists.xml"
    intermediate_xml = "artists_filled.xml"

    # Automatic fill (MusicBrainz APi)
    process_xml_dataset(original_xml, intermediate_xml) #Creates artists_filled.xml

    #Manual fill
    apply_manual_fixes(intermediate_xml) #overwrite the file artists_filled.xml

if __name__ == "__main__":
    main()
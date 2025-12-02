# normalize_artists.py
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


def prettify_xml(elem):
    """Formatta l'XML in modo leggibile"""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8')


def get_xml_text(row_element, tag_name):
    """Estrae il testo da un elemento XML"""
    el = row_element.find(tag_name)
    return el.text if el is not None else None


def set_xml_text(row_element, tag_name, value):
    """Imposta il testo di un elemento XML"""
    el = row_element.find(tag_name)
    if el is not None:
        el.text = str(value) if value is not None else ""
    else:
        # Crea l'elemento se non esiste
        new_el = ET.SubElement(row_element, tag_name)
        new_el.text = str(value) if value is not None else ""


def normalize_and_save(json_path, xml_path, output_xml_path):
    """
    Normalizza gli artisti tra JSON e XML:
    1. Carica artisti da XML
    2. Aggiorna i nomi dei primary artist dal JSON
    3. Aggiunge nuovi artisti featured non presenti nell'XML
    4. Salva tutto in un nuovo XML normalizzato
    """
    
    print("1. Caricamento XML artisti...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Dizionario ID -> elemento XML row
    artists_xml_elements = {}
    # Dizionario ID -> nome corrente
    artists_current_names = {}
    
    for row in root.findall('row'):
        artist_id = get_xml_text(row, 'id_author')
        if artist_id:
            artists_xml_elements[artist_id] = row
            artists_current_names[artist_id] = get_xml_text(row, 'name')
    
    print(f"   Caricati {len(artists_xml_elements)} artisti dall'XML")
    
    
    print("2. Caricamento JSON tracce...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   Caricate {len(data)} tracce dal JSON")
    
    
    print("3. Aggiornamento nomi Primary Artists dal JSON...")
    updated_count = 0
    
    for row in data:
        primary_id = row.get('id_artist')
        primary_name = row.get('primary_artist')
        
        if primary_id and primary_name:
            if primary_id in artists_xml_elements:
                # Aggiorna il nome nell'elemento XML
                current_name = artists_current_names.get(primary_id)
                if current_name != primary_name:
                    set_xml_text(artists_xml_elements[primary_id], 'name', primary_name)
                    artists_current_names[primary_id] = primary_name
                    updated_count += 1
    
    print(f"   Aggiornati {updated_count} nomi di primary artists")
    
    
    print("4. Creazione mappa nome -> ID...")
    name_to_id_map = {}
    for aid, name in artists_current_names.items():
        if name:
            name_to_id_map[name.strip().lower()] = aid
    
    
    print("5. Gestione Featured Artists...")
    new_artist_counter = 1
    new_artists_added = 0
    
    for row in data:
        feat_str = row.get('featured_artists')
        if feat_str:
            feats = [x.strip() for x in feat_str.split(',')]
            for f_name in feats:
                if not f_name:
                    continue
                
                f_key = f_name.lower()
                
                # Se il featured artist non esiste, crealo
                if f_key not in name_to_id_map:
                    new_id = f"ART_NEW_{new_artist_counter:04d}"
                    new_artist_counter += 1
                    
                    # Crea nuovo elemento XML
                    new_row = ET.SubElement(root, 'row')
                    
                    # Aggiungi i campi base
                    set_xml_text(new_row, 'id_author', new_id)
                    set_xml_text(new_row, 'name', f_name)
                    set_xml_text(new_row, 'gender', 'Unknown')
                    set_xml_text(new_row, 'birth_date', None)
                    set_xml_text(new_row, 'birth_place', None)
                    set_xml_text(new_row, 'nationality', None)
                    set_xml_text(new_row, 'description', 'Auto-generated from featured artists')
                    set_xml_text(new_row, 'country', None)
                    set_xml_text(new_row, 'region', None)
                    set_xml_text(new_row, 'province', None)
                    set_xml_text(new_row, 'latitude', '0.0')
                    set_xml_text(new_row, 'longitude', '0.0')
                    set_xml_text(new_row, 'active_start', None)
                    set_xml_text(new_row, 'active_end', None)
                    
                    # Aggiorna le strutture dati
                    artists_xml_elements[new_id] = new_row
                    artists_current_names[new_id] = f_name
                    name_to_id_map[f_key] = new_id
                    
                    new_artists_added += 1
    
    print(f"   Aggiunti {new_artists_added} nuovi featured artists")
    
    
    print(f"6. Salvataggio XML normalizzato in: {output_xml_path}")
    
    # Salva con formattazione pulita
    xml_bytes = prettify_xml(root)
    with open(output_xml_path, 'wb') as f:
        f.write(xml_bytes)
    
    print(f"\n✅ Normalizzazione completata!")
    print(f"   - Totale artisti finali: {len(artists_xml_elements)}")
    print(f"   - Primary artists aggiornati: {updated_count}")
    print(f"   - Featured artists aggiunti: {new_artists_added}")
    
    return artists_xml_elements, name_to_id_map


if __name__ == "__main__":
    # Configurazione percorsi
    INPUT_JSON = 'track_mood_noduplicati_refactoringids.json'
    INPUT_XML = 'artists.xml'
    OUTPUT_XML = 'artists_normalized.xml'
    
    import os
    
    # Verifica esistenza file
    if not os.path.exists(INPUT_JSON):
        print(f"❌ Errore: File {INPUT_JSON} non trovato.")
        exit(1)
    
    if not os.path.exists(INPUT_XML):
        print(f"❌ Errore: File {INPUT_XML} non trovato.")
        exit(1)
    
    try:
        normalize_and_save(INPUT_JSON, INPUT_XML, OUTPUT_XML)
    except Exception as e:
        print(f"❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()

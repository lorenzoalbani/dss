import json
# Carica il JSON
with open('dati_con_iddi.json', 'r', encoding='utf-8') as f:
    data = json.load(f)  # data = lista di dict

album_to_id = {}
next_id = 1

for item in data:
    album = item['album']
    if album not in album_to_id:
        album_to_id[album] = f'AL{str(next_id).zfill(6)}'
        next_id += 1
    item['id_album'] = album_to_id[album]

# Salva il JSON modificato
with open('dati_con_iddi_album.json', 'w') as f:
    json.dump(data, f, indent=2)

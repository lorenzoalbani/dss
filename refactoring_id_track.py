import json

# Carica il JSON
with open('track_mood_noduplicati.json', 'r', encoding='utf-8') as f:
    data = json.load(f)  # data = lista di dict
    
# Opzione 1: con zfill()
for idx, item in enumerate(data, start=1):
    item['id'] = 'TR' + str(idx).zfill(6)

# Salva il JSON modificato
with open('dati_con_iddi.json', 'w') as f:
    json.dump(data, f, indent=2)

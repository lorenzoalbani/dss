import json

# Carica il file JSON
with open('tracks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Rimuovi duplicati basati su title e primary_artist
seen = set()
cleaned_data = []

for item in data:
    key = (item['title'], item['primary_artist'])
    
    if key not in seen:
        seen.add(key)
        cleaned_data.append(item)

# Salva il JSON pulito
with open('tracks_noduplicati.json', 'w') as f:
    json.dump(cleaned_data, f, indent=2)

print(f"Originali: {len(data)}, Dopo pulizia: {len(cleaned_data)}")

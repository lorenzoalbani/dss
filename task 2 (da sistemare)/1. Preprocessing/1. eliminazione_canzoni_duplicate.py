import json

#Load the file
with open('tracks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

#Remove duplicates based on title and primary artist
seen = set()
cleaned_data = []

for item in data:
    key = (item['title'], item['primary_artist'])
    
    if key not in seen:
        seen.add(key)
        cleaned_data.append(item)

#Save the new cleand file
with open('tracks_noduplicati.json', 'w') as f:
    json.dump(cleaned_data, f, indent=2)

print(f"Original: {len(data)}, Final: {len(cleaned_data)}")

import json

# load the file
with open('tracks_noduplicati.json', 'r', encoding='utf-8') as f:
    data = json.load(f)  # data = lista di dict
    
#.zfill(6)  takes the number, transforms it into a string and adds as many 0 to the left as needed to reach a total of 6 chars
for idx, item in enumerate(data, start=1):
    item['id'] = 'TR' + str(idx).zfill(6)

#Save the new updated file
with open('tracks_noduplicati_idt.json', 'w') as f:
    json.dump(data, f, indent=2)

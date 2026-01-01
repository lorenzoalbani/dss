#questo script filla i missing values per le features melodiche

import json

# definisco le features su cui lavorare
FEATURES = ['bpm', 'rolloff', 'flux', 'rms', 'flatness', 'spectral_complexity', 'pitch', 'loudness']

def load_data(filepath): #carico il JSON file
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath): #salvo in un json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def calculate_artist_means(data, features): # Calcolo la media delle feature audio per ogni artista
    
    stats = {}

    for track in data:
        artist = track.get('primary_artist')
        
        #filtro le canzoni senza artist
        if not artist:
            continue

        #se l'artista non esiste creo la chiave
        if artist not in stats:
            stats[artist] = {}

        for feature in features:
            val = track.get(feature)
            
            #filtro i None
            if val is not None:
                #inizializzo la feature per l'artista se non esiste
                if feature not in stats[artist]:
                    stats[artist][feature] = {'sum': 0.0, 'count': 0}
                
                stats[artist][feature]['sum'] += val
                stats[artist][feature]['count'] += 1

    # Calcolo le medie finali
    means = {}
    for artist, feats in stats.items():
        means[artist] = {}
        for feature, values in feats.items():
            if values['count'] > 0:
                means[artist][feature] = values['sum'] / values['count']
    
    return means

def impute_missing_values(data, artist_means, features): #Rimpiazzo i valori nulli con le medie
    imputed_count = 0
    
    for track in data:
        artist = track.get('primary_artist')
        
        #Fillo solo se gli artisti sono validi (non None)
        if not artist or artist not in artist_means:
            continue

        for feature in features:
            val = track.get(feature)
            
            if val is None:
                mean_val = artist_means[artist].get(feature)
                
                if mean_val is not None:
                    track[feature] = mean_val
                    imputed_count += 1
                    
    return imputed_count

def main():
    input_file = 'tracks_with_yt.json'
    output_file = 'tracks_filled.json'

    print(f"Lettura file: {input_file}...")
    try:
        data = load_data(input_file)
    except FileNotFoundError:
        print("Error: File not found.")
        return


    # Calcolo le medie
    artist_means = calculate_artist_means(data, FEATURES)
    
    #riempio i missing values
    filled_values = impute_missing_values(data, artist_means, FEATURES)

    print(f"Finish. Total filled values: {filled_values}")

    # salvo
    save_data(data, output_file)
    print(f"Saved in: {output_file}...")

if __name__ == "__main__":
    main()

#This script fills the missing values for melodic features

import json

# Definizione delle features su cui lavorare
FEATURES = ['bpm', 'rolloff', 'flux', 'rms', 'flatness', 'spectral_complexity', 'pitch', 'loudness']

def load_data(filepath): #Upload the JSON file into a dictionary list.
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath): #Save the dictionary list to a JSON file.
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def calculate_artist_means(data, features): #Calculate the average of the features for each artist using standard dictionaries.
    
    stats = {}

    for track in data:
        artist = track.get('primary_artist')
        
        #Filter tracks without artist 
        if not artist:
            continue

        #If the artist doesn't exist create the key
        if artist not in stats:
            stats[artist] = {}

        for feature in features:
            val = track.get(feature)
            
            #Filter None values
            if val is not None:
                #Initialize the feature for the artist if it doesn't exist
                if feature not in stats[artist]:
                    stats[artist][feature] = {'sum': 0.0, 'count': 0}
                
                stats[artist][feature]['sum'] += val
                stats[artist][feature]['count'] += 1

    # Compute final averages
    means = {}
    for artist, feats in stats.items():
        means[artist] = {}
        for feature, values in feats.items():
            if values['count'] > 0:
                means[artist][feature] = values['sum'] / values['count']
    
    return means

def impute_missing_values(data, artist_means, features): #Replaces None values ​​in the original dataset using the calculated means.
    imputed_count = 0
    
    for track in data:
        artist = track.get('primary_artist')
        
        #Fill just for valid artists
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


    # Compute averages
    artist_means = calculate_artist_means(data, FEATURES)
    
    #Fill missing values
    filled_values = impute_missing_values(data, artist_means, FEATURES)

    print(f"Finish. Total filled values: {filled_values}")

    # 3. Salvataggio
    save_data(data, output_file)
    print(f"Saved in: {output_file}...")

if __name__ == "__main__":
    main()
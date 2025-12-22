from youtubesearchpython import VideosSearch
import json
import time
from datetime import datetime
from tqdm import tqdm


def search_youtube_video_id(title, artist, max_retries=3):
    """
    Cerca un video youtube e ritorna l'ID
    """
    query = f"{artist} {title} official video"
    
    for attempt in range(max_retries):
        try:
            videos_search = VideosSearch(query, limit=1)
            results = videos_search.result()
            
            if results and 'result' in results and len(results['result']) > 0:
                video_id = results['result'][0]['id']
                return video_id
            else:
                return None
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                print(f"Errore per '{artist} - {title}': {e}")
                return None
    
    return None


def add_youtube_ids_to_list(songs_list, title_key='title', artist_key='primary_artist', 
                            checkpoint_every=100, checkpoint_file='youtube_ids_checkpoint.json'):
    """
        Aggiunge l'ID del video YouTube a ogni canzone nella lista, ho messo anche la barra di progresso tqdm.

        parametri passati:
            songs_list (list): Lista di dizionari con le canzoni
            title_key (str): Chiave per il titolo nel dizionario
            artist_key (str): Chiave per l'artista nel dizionario
            checkpoint_every (int): Salva checkpoint ogni X canzoni elaborate
            checkpoint_file (str): Nome file JSON per i salvataggi intermedi

        ritorna:
            Lista aggiornata con 'youtube_video_id' per ogni traccia
    """
    total = len(songs_list)
    start_time = datetime.now()
    found_count = 0
    
    print(f"Inizio scraping di {total} canzoni...")
    print(f"Ora di inizio: {start_time.strftime('%H:%M:%S')}\n")
    
    #itero sopra la lista
    for idx, song in enumerate(tqdm(songs_list, 
                                     desc="Scraping YouTube IDs", 
                                     unit="song",
                                     colour="green",
                                     ncols=100)):
        
        #Skippa se gia trovato l'ID (nel caso fosse rimandato il codice dopo averlo interrotto)
        if song.get('youtube_video_id') is not None:
            found_count += 1
            continue
        
        #cerca l'ID
        video_id = search_youtube_video_id(song[title_key], song[artist_key])
        song['youtube_video_id'] = video_id
        
        if video_id:
            found_count += 1
        
        #Checkpoint
        if (idx + 1) % checkpoint_every == 0 and idx > 0:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(songs_list, f, ensure_ascii=False, indent=2)
            tqdm.write(f"Checkpoint salvato: {found_count}/{idx+1} trovati")
        
        # rate limit
        time.sleep(1.5)
    
    #Salvataggio finale
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(songs_list, f, ensure_ascii=False, indent=2)
    
    elapsed_total = (datetime.now() - start_time).total_seconds() / 60
    
    print(f"\n{'='*60}")
    print(f"Scraping completato!")
    print(f"Tempo totale: {elapsed_total:.1f} minuti")
    print(f"Video ID trovati: {found_count}/{total} ({found_count/total*100:.1f}%)")
    print(f"{'='*60}\n")
    
    return songs_list


if __name__ == '__main__':
    # Carico il file originale
    with open('tracks.json', 'r', encoding='utf-8') as f:
        songs = json.load(f)
    
    #Scraping
    songs = add_youtube_ids_to_list(
        songs, 
        title_key='title',
        artist_key='primary_artist'
    )

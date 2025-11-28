from youtubesearchpython import VideosSearch
import json
import time
from datetime import datetime
from tqdm import tqdm


def search_youtube_video_id(title, artist, max_retries=3):
    """
    Cerca un video YouTube e ritorna il video ID
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
    Aggiunge 'youtube_video_id' ad ogni dizionario nella lista con progress bar tqdm
    
    Args:
        songs_list: Lista di dizionari con le canzoni
        title_key: Chiave per il titolo nel dizionario
        artist_key: Chiave per l'artista nel dizionario
        checkpoint_every: Ogni quante canzoni salvare un checkpoint
        checkpoint_file: Nome del file JSON per i checkpoint
    
    Returns:
        Lista aggiornata con gli ID YouTube
    """
    total = len(songs_list)
    start_time = datetime.now()
    found_count = 0
    
    print(f"Inizio scraping di {total} canzoni...")
    print(f"Ora di inizio: {start_time.strftime('%H:%M:%S')}\n")
    
    # Usa tqdm per iterare sulla lista
    for idx, song in enumerate(tqdm(songs_list, 
                                     desc="Scraping YouTube IDs", 
                                     unit="song",
                                     colour="green",
                                     ncols=100)):
        
        # Salta se già processato
        if song.get('youtube_video_id') is not None:
            found_count += 1
            continue
        
        # Cerca il video ID
        video_id = search_youtube_video_id(song[title_key], song[artist_key])
        song['youtube_video_id'] = video_id
        
        if video_id:
            found_count += 1
        
        # Checkpoint periodico
        if (idx + 1) % checkpoint_every == 0 and idx > 0:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(songs_list, f, ensure_ascii=False, indent=2)
            tqdm.write(f"✓ Checkpoint salvato: {found_count}/{idx+1} trovati")
        
        # Rate limiting
        time.sleep(1.5)
    
    # Salvataggio finale
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(songs_list, f, ensure_ascii=False, indent=2)
    
    elapsed_total = (datetime.now() - start_time).total_seconds() / 60
    
    print(f"\n{'='*60}")
    print(f"✓ Scraping completato!")
    print(f"Tempo totale: {elapsed_total:.1f} minuti")
    print(f"Video ID trovati: {found_count}/{total} ({found_count/total*100:.1f}%)")
    print(f"{'='*60}\n")
    
    return songs_list


if __name__ == '__main__':
    # 1. Carica il JSON iniziale
    with open('tracks.json', 'r', encoding='utf-8') as f:
        songs = json.load(f)
    
    # 2. Esegui lo scraping
    songs = add_youtube_ids_to_list(
        songs, 
        title_key='title',
        artist_key='primary_artist'
    )

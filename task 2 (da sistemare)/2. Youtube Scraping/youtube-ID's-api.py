from youtubesearchpython import VideosSearch
import json
import time
from datetime import datetime
from tqdm import tqdm


def search_youtube_video_id(title, artist, max_retries=3):
    """
    Search for a YouTube video and return the video ID
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
    Adds 'youtube_video_id' to each dictionary in the list with progress bar tqdm
    
    Args:
        songs_list: List of song dictionaries
        title_key: Key for the title in the dictionary
        artist_key: Key for the artist in the dictionary
        checkpoint_every: How often to save a checkpoint for each song
        checkpoint_file: Name of the JSON file for the checkpoints
    
    Returns:
        Updated list with youtube IDs
    """
    total = len(songs_list)
    start_time = datetime.now()
    found_count = 0
    
    print(f"Inizio scraping di {total} canzoni...")
    print(f"Ora di inizio: {start_time.strftime('%H:%M:%S')}\n")
    
    #Use tqdm to iterate over the list
    for idx, song in enumerate(tqdm(songs_list, 
                                     desc="Scraping YouTube IDs", 
                                     unit="song",
                                     colour="green",
                                     ncols=100)):
        
        #Skip if already processed
        if song.get('youtube_video_id') is not None:
            found_count += 1
            continue
        
        #Look for the video id
        video_id = search_youtube_video_id(song[title_key], song[artist_key])
        song['youtube_video_id'] = video_id
        
        if video_id:
            found_count += 1
        
        #Periodic checkpoint
        if (idx + 1) % checkpoint_every == 0 and idx > 0:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(songs_list, f, ensure_ascii=False, indent=2)
            tqdm.write(f"✓ Checkpoint salvato: {found_count}/{idx+1} trovati")
        
        # Rate limiting
        time.sleep(1.5)
    
    #Final save
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
    # Load the original file
    with open('tracks.json', 'r', encoding='utf-8') as f:
        songs = json.load(f)
    
    #Scraping
    songs = add_youtube_ids_to_list(
        songs, 
        title_key='title',
        artist_key='primary_artist'
    )

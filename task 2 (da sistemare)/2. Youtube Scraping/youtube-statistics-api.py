from googleapiclient.discovery import build
import json
from tqdm import tqdm
import time

# La tua API Key
API_KEY = "AIzaSyA9BMJiGhlfOT7uTsskle7Rc_YcClbxWmM"

# Crea il client YouTube
youtube = build('youtube', 'v3', developerKey=API_KEY)


def get_video_statistics_batch(video_ids):
    """
    Recupera statistiche per fino a 50 video ID in una singola chiamata API.
    Ritorna un dizionario con video_id come chiave.
    """
    # YouTube API accetta max 50 IDs per chiamata
    video_ids_str = ','.join(video_ids)
    
    try:
        request = youtube.videos().list(
            part='statistics,contentDetails,snippet',
            id=video_ids_str
        )
        response = request.execute()
        
        stats_dict = {}
        
        for item in response.get('items', []):
            video_id = item['id']
            stats = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            snippet = item.get('snippet', {})
            
            stats_dict[video_id] = {
                'yt_view_count': int(stats.get('viewCount', 0)),
                'yt_like_count': int(stats.get('likeCount', 0)),
                'yt_comment_count': int(stats.get('commentCount', 0)),
                'yt_duration': content_details.get('duration', None),
                'yt_definition': content_details.get('definition', None),
                'yt_published_at': snippet.get('publishedAt', None),
                'yt_category_id': snippet.get('categoryId', None)
            }
        
        return stats_dict
    
    except Exception as e:
        print(f"Errore nel recupero batch: {e}")
        return {}


def enrich_with_youtube_statistics(songs_list, video_id_key='youtube_video_id', 
                                   batch_size=50, output_file='youtube_stats_enriched.json'):
    """
    Arricchisce la lista di canzoni con statistiche YouTube usando batch API calls.
    
    Args:
        songs_list: Lista di dizionari con le canzoni
        video_id_key: Chiave per l'ID YouTube nel dizionario
        batch_size: Numero di video per batch (max 50)
        output_file: Nome del file JSON di output
    
    Returns:
        Lista aggiornata con le statistiche YouTube
    """
    # Filtra solo i video ID validi (non None/null)
    video_ids_list = [song[video_id_key] for song in songs_list 
                      if song.get(video_id_key) is not None]
    
    print(f"Totale video ID da processare: {len(video_ids_list)}")
    print(f"Batch da {batch_size} video per chiamata API")
    print(f"Chiamate API necessarie: {len(video_ids_list) // batch_size + 1}")
    print(f"Quota consumata stimata: ~{len(video_ids_list) // batch_size + 1} units\n")
    
    # Processa in batch
    all_stats = {}
    
    for i in tqdm(range(0, len(video_ids_list), batch_size), 
                  desc="Recupero statistiche YouTube", 
                  unit="batch",
                  colour="blue"):
        
        batch = video_ids_list[i:i+batch_size]
        batch_stats = get_video_statistics_batch(batch)
        all_stats.update(batch_stats)
        
        # Piccola pausa per rispettare rate limits (opzionale ma consigliato)
        time.sleep(0.2)
    
    print(f"\n✓ Recuperate statistiche per {len(all_stats)} video su {len(video_ids_list)}")
    
    # Aggiungi le statistiche a ogni canzone nella lista
    for song in songs_list:
        video_id = song.get(video_id_key)
        
        if video_id and video_id in all_stats:
            # Aggiungi tutte le statistiche al dizionario della canzone
            song.update(all_stats[video_id])
        else:
            # Aggiungi campi None se non ci sono statistiche
            song['yt_view_count'] = None
            song['yt_like_count'] = None
            song['yt_comment_count'] = None
            song['yt_duration'] = None
            song['yt_definition'] = None
            song['yt_published_at'] = None
            song['yt_category_id'] = None
    
    # Salva il risultato
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(songs_list, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Dataset arricchito salvato in: {output_file}")
    
    # Statistiche finali
    view_count = sum(1 for s in songs_list if s.get('yt_view_count') is not None)
    like_count = sum(1 for s in songs_list if s.get('yt_like_count') is not None)
    comment_count = sum(1 for s in songs_list if s.get('yt_comment_count') is not None)
    
    print(f"\nStatistiche recupero:")
    print(f"  - View count trovati: {view_count}/{len(songs_list)}")
    print(f"  - Like count trovati: {like_count}/{len(songs_list)}")
    print(f"  - Comment count trovati: {comment_count}/{len(songs_list)}")
    
    return songs_list


if __name__ == '__main__':
    # 1. Carica il JSON con gli ID YouTube (dal checkpoint o dal file finale dello scraping)
    with open('youtube_ids_checkpoint.json', 'r', encoding='utf-8') as f:
        songs = json.load(f)
    
    # 2. Arricchisci con le statistiche YouTube
    songs_enriched = enrich_with_youtube_statistics(
        songs, 
        video_id_key='youtube_video_id',
        batch_size=50,
        output_file='tracks_with_youtube_stats.json'
    )
    
    print("\n✓ Processo completato!")

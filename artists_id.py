import pandas as pd

def check_referential_integrity():
    print("--- VERIFICA INTEGRITÀ REFERENZIALE (TRACKS vs ARTISTS) ---\n")

    # 1. Caricamento File
    try:
        df_tracks = pd.read_json('tracks_with_artists_id.json')
        df_artists = pd.read_xml('artists_with_id.xml')
        print(f"File caricati: {len(df_tracks)} tracce, {len(df_artists)} artisti.")
    except Exception as e:
        print(f"Errore caricamento: {e}")
        return

    # 2. Identificazione colonna ID nell'XML
    # Gestiamo sia il caso 'id' che 'id_author'
    xml_id_col = 'id_author' if 'id_author' in df_artists.columns else 'id'
    print(f"Colonna ID rilevata nell'XML: '{xml_id_col}'")

    # Creiamo il SET degli ID validi (La "Fonte di Verità")
    valid_ids_set = set(df_artists[xml_id_col].astype(str))

    # --- CHECK A: PRIMARY ARTISTS ---
    print("\n[A] Controllo Primary Artists...")
    
    # Prendiamo gli ID unici dalle tracce
    primary_ids_tracks = set(df_tracks['id_artist'].astype(str))
    
    # Calcoliamo la differenza: (ID nelle Tracce) - (ID Validi)
    missing_primary = primary_ids_tracks - valid_ids_set
    
    if len(missing_primary) == 0:
        print("✅ PASSATO: Tutti i Primary Artists esistono nel file XML.")
    else:
        print(f"❌ FALLITO: Trovati {len(missing_primary)} ID Primary che NON esistono nell'XML!")
        print(f"   Esempi mancanti: {list(missing_primary)[:5]}")

    # --- CHECK B: FEATURED ARTISTS ---
    print("\n[B] Controllo Featured Artists...")
    
    # 1. Prendiamo la colonna, rimuoviamo i nulli
    # 2. Dividiamo le stringhe per virgola
    # 3. 'Esplodiamo' le liste in righe singole
    # 4. Rimuoviamo spazi bianchi
    feat_ids_series = df_tracks['featured_artists'].dropna().astype(str).str.split(',').explode().str.strip()
    
    # Creiamo il set degli ID unici trovati nei featured
    feat_ids_tracks = set(feat_ids_series)
    
    # Calcoliamo la differenza
    missing_featured = feat_ids_tracks - valid_ids_set
    
    if len(missing_featured) == 0:
        print("✅ PASSATO: Tutti i Featured Artists esistono nel file XML.")
    else:
        print(f"❌ FALLITO: Trovati {len(missing_featured)} ID/Stringhe nei Featured che NON esistono nell'XML!")
        print(f"   Esempi mancanti: {list(missing_featured)[:5]}")
        print("   (Se vedi dei Nomi invece di ID tipo ART..., significa che il mapping non ha funzionato per quei nomi)")

    # --- RISULTATO FINALE ---
    print("\n--- ESITO ---")
    if len(missing_primary) == 0 and len(missing_featured) == 0:
        print("🟢 TUTTO OK: I file sono perfettamente sincronizzati.")
    else:
        print("🔴 ERRORI TROVATI: I file non sono coerenti.")

if __name__ == "__main__":
    check_referential_integrity()
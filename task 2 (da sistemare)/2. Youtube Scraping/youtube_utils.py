def get_virality_tier(view_count):
    """
    Riceve il numero di visualizzazioni (come stringa o numero)
    e restituisce una categoria di business.
    """
    # Gestione valori nulli o errori
    if view_count is None or view_count == "":
        return "Unknown"
    
    try:
        # Convertiamo in float
        views = int(float(view_count))
    except ValueError:
        return "Unknown"

    # Logica di Business
    if views >= 50_000_000:
        return "Global Hit"       # Oltre 50M: Successo mondiale
    elif views >= 10_000_000:
        return "Mainstream"       # 10M - 50M: Molto famoso
    elif views >= 1_000_000:
        return "Trending"         # 1M - 10M: Sta andando bene
    elif views >= 100_000:
        return "Emerging"         # 100k - 1M: Artista emergente
    else:
        return "Niche"            # Sotto 100k: Nicchia / Underground
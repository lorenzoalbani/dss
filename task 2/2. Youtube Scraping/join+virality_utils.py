def get_virality_tier(view_count):

    # controllo null o errori
    if view_count is None or view_count == "":
        return "Unknown"
    
    try:
        # converto in float
        views = int(float(view_count))
    except ValueError:
        return "Unknown"

    # discretizzazione
    if views >= 50_000_000:
        return "Global Hit"       # > 50M
    elif views >= 10_000_000:
        return "Mainstream"       # 10M - 50M
    elif views >= 1_000_000:
        return "Trending"         # 1M - 10M
    elif views >= 100_000:
        return "Emerging"         # 100k - 1M
    else:
        return "Niche"            # < 100k

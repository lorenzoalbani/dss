def get_virality_tier(view_count):
    """
    Receives the number of views (as a string or number)
    and returns a business category.
    """
    # Handling null values ​​or errors
    if view_count is None or view_count == "":
        return "Unknown"
    
    try:
        # Convert to floats
        views = int(float(view_count))
    except ValueError:
        return "Unknown"

    # Business logic
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
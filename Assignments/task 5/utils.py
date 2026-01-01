# utils.py
def get_season(month):
    if month in [12, 1, 2]: return 'Winter'
    elif month in [3, 4, 5]: return 'Spring'
    elif month in [6, 7, 8]: return 'Summer'
    else: return 'Autumn'

def get_quarter(month):
    return (month - 1) // 3 + 1

def safe_int(value):
    try: return int(float(value))
    except (ValueError, TypeError): return 0

def safe_float(value):
    if value is None: return 0.0
    return float(value)

def clean_text(text):
    if text is None: return ""
    return str(text).replace('\n', ' ').replace('\r', '')
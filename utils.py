import os
import json

from pathlib import Path
from urllib.parse import urlparse, urlunparse

ENCODING = "utf-8"

def load_json_file(filename):
    """Loads a JSON file and returns a dictionary. Returns empty dict if not found."""
    file_path = Path(filename)
    if not file_path.is_file():
        return {}    
    try:
        with open(file_path, "r", encoding=ENCODING) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_json_file(data, file):
    """Saves a dictionary to a JSON file safely."""
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "w", encoding=ENCODING) as f:
        json.dump(data, f, ensure_ascii=False)

def normalize_url(url) -> str:
    """Strips query parameters and fragments from a URL and handles casing."""
    parsed_url = urlparse(url)
    return urlunparse(parsed_url._replace(scheme=parsed_url.scheme.lower(),fragment="", query=""))
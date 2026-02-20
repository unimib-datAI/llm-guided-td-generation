import json
from pathlib import Path

def load_pages(directory: Path):
    pages = []
    for file in directory.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            pages.append(json.load(f))
    return pages
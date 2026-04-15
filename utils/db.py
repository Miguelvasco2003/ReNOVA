import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "images"


def ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)


# ── Users ──────────────────────────────────────────────────────────────────

def load_users() -> dict:
    path = DATA_DIR / "users_db.json"
    if not path.exists():
        _save_json(path, {"users": {}})
    return _load_json(path)


def save_users(data: dict):
    _save_json(DATA_DIR / "users_db.json", data)


# ── Listings ───────────────────────────────────────────────────────────────

def load_listings() -> dict:
    path = DATA_DIR / "listings_db.json"
    if not path.exists():
        _save_json(path, {"listings": []})
    return _load_json(path)


def save_listings(data: dict):
    _save_json(DATA_DIR / "listings_db.json", data)


# ── Helpers ────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

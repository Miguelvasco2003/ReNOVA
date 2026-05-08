import json
from pathlib import Path

BASE_DIR   = Path(__file__).parent.parent
DATA_DIR   = BASE_DIR / "data"
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


def get_user(student_id: str) -> dict | None:
    return load_users()["users"].get(student_id)


# ── Listings ───────────────────────────────────────────────────────────────

def load_listings() -> dict:
    path = DATA_DIR / "listings_db.json"
    if not path.exists():
        _save_json(path, {"listings": []})
    return _load_json(path)


def save_listings(data: dict):
    _save_json(DATA_DIR / "listings_db.json", data)


def get_listing_images(listing: dict) -> list[str]:
    """Return list of image paths, handling both old (image_path) and new (images) format."""
    if listing.get("images"):
        return [p for p in listing["images"] if p]
    if listing.get("image_path"):
        return [listing["image_path"]]
    return []


# ── Profile photos ─────────────────────────────────────────────────────────

def get_profile_photo_path(student_id: str) -> Path | None:
    """Return Path to profile photo if it exists, else None."""
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        p = IMAGES_DIR / f"profile_{student_id}{ext}"
        if p.exists():
            return p
    return None


def save_profile_photo(student_id: str, ext: str, data: bytes) -> str:
    """Save profile photo bytes. Deletes old photo first. Returns relative path."""
    for old_ext in [".jpg", ".jpeg", ".png", ".webp"]:
        old = IMAGES_DIR / f"profile_{student_id}{old_ext}"
        if old.exists():
            old.unlink()
    filename = f"profile_{student_id}{ext}"
    path = IMAGES_DIR / filename
    path.write_bytes(data)
    return f"images/{filename}"


# ── Favorites ──────────────────────────────────────────────────────────────

def toggle_favorite(student_id: str, listing_id: str) -> list:
    """Toggle listing in user favorites. Returns updated favorites list."""
    db = load_users()
    user = db["users"].get(student_id, {})
    favs = list(user.get("favorites", []))
    if listing_id in favs:
        favs.remove(listing_id)
    else:
        favs.append(listing_id)
    user["favorites"] = favs
    db["users"][student_id] = user
    save_users(db)
    return favs


# ── Helpers ────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

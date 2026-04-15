import hashlib
from datetime import datetime
from utils.db import load_users, save_users


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(student_id: str, password: str, name: str, whatsapp: str):
    """Return (success: bool, message: str)."""
    student_id = student_id.strip()
    db = load_users()
    if student_id in db["users"]:
        return False, "This Student ID is already registered."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    db["users"][student_id] = {
        "student_id": student_id,
        "password_hash": _hash(password),
        "email": f"{student_id}@novasbe.pt",
        "name": name.strip(),
        "whatsapp": whatsapp.strip(),
        "created_at": datetime.now().isoformat(),
    }
    save_users(db)
    return True, "Account created successfully!"


def login_user(student_id: str, password: str):
    """Return (success: bool, user_dict | None)."""
    student_id = student_id.strip()
    db = load_users()
    user = db["users"].get(student_id)
    if user and user["password_hash"] == _hash(password):
        return True, user
    return False, None


def get_user(student_id: str) -> dict | None:
    return load_users()["users"].get(student_id)

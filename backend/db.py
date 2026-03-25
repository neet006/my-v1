"""
db.py — Local JSON storage engine for A.M.A.T.S.
All data lives in backend/data/ (created automatically).
"""
import os
import json
import hashlib
import uuid
from datetime import datetime

# ── Data directory: always next to this file ──────────────────────────────────
DATA_DIR      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
USERS_FILE    = os.path.join(DATA_DIR, "users.json")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")


def _ensure_data_dir():
    """Create backend/data/ if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _read_json(path, default):
    """Read a JSON file safely; return default on missing/corrupt file."""
    _ensure_data_dir()
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError, ValueError):
        # Corrupt file — back it up and return default
        try:
            os.rename(path, path + ".bak")
        except OSError:
            pass
        return default


def _write_json(path, data):
    """Write data to a JSON file atomically (write to tmp, then rename)."""
    _ensure_data_dir()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
    os.replace(tmp, path)   # atomic on all major OS


def _hash_password(password: str) -> str:
    """SHA-256 hash for password storage."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ═══════════════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════════════

def get_all_users() -> dict:
    return _read_json(USERS_FILE, {})


def get_user_by_email(email: str) -> dict | None:
    return get_all_users().get(email.strip().lower())


def create_user(name: str, email: str, password: str) -> dict:
    """
    Create and persist a new user.
    Raises ValueError if the email is already registered.
    """
    if not name or not email or not password:
        raise ValueError("Name, email, and password are all required.")
    email = email.strip().lower()
    users = get_all_users()
    if email in users:
        raise ValueError("An account with that email already exists.")
    user = {
        "id":            str(uuid.uuid4()),
        "name":          name.strip(),
        "email":         email,
        "password_hash": _hash_password(password),
        "created_at":    datetime.now().isoformat(),
    }
    users[email] = user
    _write_json(USERS_FILE, users)
    return user


def verify_user(email: str, password: str) -> dict | None:
    """Return the user dict if credentials are correct, else None."""
    user = get_user_by_email(email)
    if user and user.get("password_hash") == _hash_password(password):
        return user
    return None


# ═══════════════════════════════════════════════════════════════
# SESSIONS
# ═══════════════════════════════════════════════════════════════

DEFAULT_SESSIONS: list[dict] = [
    {
        "date":            "Today, 2:30 PM",
        "duration":        "1h 45m",
        "alerts":          2,
        "max_drowsiness":  "45%",
        "status":          "Completed",
        "status_class":    "completed",
    },
    {
        "date":            "Yesterday, 8:15 AM",
        "duration":        "3h 20m",
        "alerts":          1,
        "max_drowsiness":  "32%",
        "status":          "Completed",
        "status_class":    "completed-dark",
    },
    {
        "date":            "Dec 8, 6:45 PM",
        "duration":        "2h 10m",
        "alerts":          4,
        "max_drowsiness":  "68%",
        "status":          "High Risk",
        "status_class":    "high-risk",
    },
]


def get_sessions(user_id: str) -> list:
    """Return the session list for user_id, or demo data for new users."""
    all_sessions = _read_json(SESSIONS_FILE, {})
    return all_sessions.get(user_id, DEFAULT_SESSIONS)


def save_session(user_id: str, session_data: dict) -> None:
    """Append a new session record for user_id."""
    all_sessions = _read_json(SESSIONS_FILE, {})
    all_sessions.setdefault(user_id, list(DEFAULT_SESSIONS))
    all_sessions[user_id].insert(0, session_data)   # newest first
    _write_json(SESSIONS_FILE, all_sessions)


# ═══════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════

DEFAULT_SETTINGS: dict = {
    # Detection
    "detection_sensitivity":   75,
    "eye_closure_threshold":   3,
    "blink_rate_monitoring":   True,
    "head_pose_tracking":      True,
    "yawn_detection":          True,
    # Alerts
    "audio_alerts":            True,
    "voice_warnings":          True,
    "visual_alerts":           True,
    "vibration_alerts":        False,
    "alert_volume":            70,
    "alert_delay":             2,
    # Camera
    "camera_resolution":       "1920x1080",
    "frame_rate":              "30",
    "face_detection_mode":     "High Performance",
    "night_vision":            True,
    "auto_exposure":           True,
    # Privacy & Safety
    "emergency_contacts":      True,
    "data_logging":            True,
    "privacy_mode":            False,
    "share_anonymous_data":    True,
    "emergency_contact_phone": "",
}


def get_settings(user_id: str) -> dict:
    """Return settings for user_id merged with defaults (so new keys always exist)."""
    all_settings = _read_json(SETTINGS_FILE, {})
    merged = DEFAULT_SETTINGS.copy()
    merged.update(all_settings.get(user_id, {}))
    return merged


def save_settings(user_id: str, incoming: dict) -> None:
    """
    Persist settings for user_id.
    Merges with defaults first to prevent bad/missing values.
    Coerces types to match DEFAULT_SETTINGS so the DB stays clean.
    """
    all_settings = _read_json(SETTINGS_FILE, {})
    merged = DEFAULT_SETTINGS.copy()
    for key, default_val in DEFAULT_SETTINGS.items():
        if key not in incoming:
            continue
        val = incoming[key]
        # Type coercion — keep DB types consistent with defaults
        if isinstance(default_val, bool):
            merged[key] = bool(val)
        elif isinstance(default_val, int):
            try:
                merged[key] = int(val)
            except (ValueError, TypeError):
                pass   # keep default
        elif isinstance(default_val, str):
            merged[key] = str(val)
    all_settings[user_id] = merged
    _write_json(SETTINGS_FILE, all_settings)

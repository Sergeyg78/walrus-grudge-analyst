"""
Leaderboard Module
Stores and retrieves a shared public leaderboard blob on Walrus.
All users' stats are aggregated into a single shared blob.
"""

import json
from datetime import datetime
from typing import Optional

from utils.walrus_memory import store_memory, retrieve_memory

# Local cache file for leaderboard blob ID
LEADERBOARD_CACHE = "leaderboard_blob.txt"


def _load_leaderboard_blob_id() -> Optional[str]:
    try:
        with open(LEADERBOARD_CACHE, "r") as f:
            return f.read().strip() or None
    except Exception:
        return None


def _save_leaderboard_blob_id(blob_id: str):
    try:
        with open(LEADERBOARD_CACHE, "w") as f:
            f.write(blob_id)
    except Exception as e:
        print(f"[Leaderboard] Cache save failed: {e}")


def get_leaderboard() -> list:
    """Fetch current leaderboard from Walrus. Returns list of entries."""
    blob_id = _load_leaderboard_blob_id()
    if not blob_id:
        return []
    data = retrieve_memory(blob_id)
    if not data:
        return []
    return data.get("entries", [])


def update_leaderboard(username: str, stats: dict) -> Optional[str]:
    """
    Update or insert a user's stats on the leaderboard.
    Fetches current leaderboard, updates entry, saves new blob.
    Returns new blob_id or None on failure.
    """
    entries = get_leaderboard()

    # Update or insert
    found = False
    for entry in entries:
        if entry["username"].lower() == username.lower():
            entry["correct"]   = stats.get("correct", 0)
            entry["wrong"]     = stats.get("wrong", 0)
            entry["pending"]   = stats.get("pending", 0)
            entry["win_rate"]  = stats.get("win_rate", "0%")
            entry["last_updated"] = datetime.utcnow().isoformat() + "Z"
            found = True
            break

    if not found:
        entries.append({
            "username":     username,
            "correct":      stats.get("correct", 0),
            "wrong":        stats.get("wrong", 0),
            "pending":      stats.get("pending", 0),
            "win_rate":     stats.get("win_rate", "0%"),
            "last_updated": datetime.utcnow().isoformat() + "Z",
        })

    # Sort by correct desc, then win_rate
    entries.sort(key=lambda x: (x["correct"], int(x["win_rate"].replace("%", "") or 0)), reverse=True)

    payload = {
        "schema_version": "1.0",
        "type": "leaderboard",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "entries": entries,
    }

    blob_id = store_memory(payload)
    if blob_id:
        _save_leaderboard_blob_id(blob_id)
    return blob_id


def get_leaderboard_blob_id() -> Optional[str]:
    return _load_leaderboard_blob_id()

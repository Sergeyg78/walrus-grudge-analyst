"""
Auth Module — Username + PIN login with Walrus-backed master blob.
Each user has a "registry blob" that stores their master blob ID chain.
No external database needed — everything lives on Walrus.
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Optional, Tuple

from utils.walrus_memory import store_memory, retrieve_memory

# ── Registry key: deterministic blob lookup ────────────────────────────────────
# We derive a stable "registry ID" from username+PIN using SHA256.
# This is stored as a well-known local map (registry.json) that maps
# hashed credentials → master blob ID.
# On Streamlit Cloud, we use st.session_state + Walrus to persist it.

REGISTRY_FILE = "registry.json"


def _hash_credentials(username: str, pin: str) -> str:
    """SHA256 of username:pin — used as registry key."""
    raw = f"{username.strip().lower()}:{pin.strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _load_registry() -> dict:
    """Load local registry mapping cred_hash → master_blob_id."""
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_registry(registry: dict):
    """Persist registry to local file."""
    try:
        with open(REGISTRY_FILE, "w") as f:
            json.dump(registry, f)
    except Exception as e:
        print(f"[Auth] Registry save failed: {e}")


def register_user(username: str, pin: str) -> Tuple[bool, str]:
    """
    Register a new user. Returns (success, message).
    Creates an empty master blob on Walrus and stores the blob ID in registry.
    """
    if len(pin) != 4 or not pin.isdigit():
        return False, "PIN must be exactly 4 digits."
    if len(username.strip()) < 2:
        return False, "Username must be at least 2 characters."

    cred_hash = _hash_credentials(username, pin)
    registry = _load_registry()

    if cred_hash in registry:
        return False, "Username already exists. Try logging in."

    # Create empty master state blob
    master_payload = _build_master_blob(username, [], [], [], {
        "correct": 0, "wrong": 0, "pending": 0, "win_rate": "0%"
    }, previous_blob_id=None)

    blob_id = store_memory(master_payload)
    if not blob_id:
        return False, "Could not connect to Walrus testnet. Try again."

    registry[cred_hash] = {
        "username": username.strip(),
        "master_blob_id": blob_id,
        "created": datetime.utcnow().isoformat() + "Z",
        "blob_chain": [blob_id],
    }
    _save_registry(registry)
    return True, blob_id


def login_user(username: str, pin: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Login an existing user.
    Returns (success, message, state_dict_or_None).
    """
    cred_hash = _hash_credentials(username, pin)
    registry = _load_registry()

    if cred_hash not in registry:
        return False, "Username or PIN not found. Please register first.", None

    entry = registry[cred_hash]
    master_blob_id = entry["master_blob_id"]

    payload = retrieve_memory(master_blob_id)
    if not payload:
        # Try last known blob in chain
        chain = entry.get("blob_chain", [master_blob_id])
        for bid in reversed(chain):
            payload = retrieve_memory(bid)
            if payload:
                break

    if not payload:
        return False, "Could not retrieve your data from Walrus. Try again.", None

    return True, master_blob_id, payload


def update_user_blob(username: str, pin: str, new_blob_id: str):
    """Update the master blob ID for a user after a save."""
    cred_hash = _hash_credentials(username, pin)
    registry = _load_registry()
    if cred_hash in registry:
        registry[cred_hash]["master_blob_id"] = new_blob_id
        chain = registry[cred_hash].get("blob_chain", [])
        if new_blob_id not in chain:
            chain.append(new_blob_id)
        registry[cred_hash]["blob_chain"] = chain[-20:]  # keep last 20
        _save_registry(registry)


def get_all_users() -> list:
    """Return list of all registered usernames (for leaderboard)."""
    registry = _load_registry()
    return [v["username"] for v in registry.values()]


def _build_master_blob(
    username: str,
    predictions: list,
    grudge_log: list,
    hot_takes: list,
    stats: dict,
    previous_blob_id: Optional[str],
) -> dict:
    return {
        "schema_version": "2.0",
        "username": username,
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "previous_blob_id": previous_blob_id,
        "stats": stats,
        "predictions": predictions,
        "grudge_log": grudge_log,
        "hot_takes": hot_takes,
    }

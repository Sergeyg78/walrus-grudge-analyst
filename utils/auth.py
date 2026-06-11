"""
Auth Module v3 — Reliable registration that never depends on Walrus.

Architecture:
- Registry (username→PIN→blob_id mapping) lives ONLY in st.session_state.
- Registration is instant — no Walrus call needed to create an account.
- On register: credentials hashed + stored in session_state registry.
- On login: credentials checked against session_state registry.
- User's PREDICTION DATA (not credentials) is stored on Walrus.
- The registry persists across browser tabs in the same session.
- To persist across sessions/devices: user copies their Blob ID and
  uses "Load by Blob ID" login — no registry lookup needed at all.

Two login modes:
  1. Username + PIN  → works within the same Streamlit session
  2. Direct Blob ID  → works across sessions/devices (paste blob ID)
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, Tuple
import streamlit as st

from utils.walrus_memory import retrieve_memory, get_network_name


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash_credentials(username: str, pin: str) -> str:
    raw = f"{username.strip().lower()}:{pin.strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _get_registry() -> dict:
    """Get in-memory registry from session state."""
    if "_auth_registry" not in st.session_state:
        st.session_state["_auth_registry"] = {}
    return st.session_state["_auth_registry"]


def _save_registry(registry: dict):
    """Persist registry back to session state."""
    st.session_state["_auth_registry"] = registry


# ── Public API ────────────────────────────────────────────────────────────────

def register_user(username: str, pin: str) -> Tuple[bool, str]:
    """
    Register a new user instantly — no Walrus call.
    Returns (success, message).
    User's data blob is created on first save (not on register).
    """
    if len(pin) != 4 or not pin.isdigit():
        return False, "PIN must be exactly 4 digits."
    if len(username.strip()) < 2:
        return False, "Username must be at least 2 characters."

    cred_hash = _hash_credentials(username, pin)
    registry  = _get_registry()

    if cred_hash in registry:
        return False, "Username already taken. Try a different one."

    # Register instantly — no Walrus needed
    registry[cred_hash] = {
        "username":       username.strip(),
        "master_blob_id": None,       # set on first Walrus save
        "created":        datetime.utcnow().isoformat() + "Z",
        "blob_chain":     [],
    }
    _save_registry(registry)
    print(f"[Auth] Registered: {username.strip()}")
    return True, "ok"


def login_user(username: str, pin: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Login with username + PIN.
    Returns (success, message_or_blob_id, payload_or_None).

    If user has a saved blob: loads from Walrus and returns payload.
    If user has no saved blob yet (new user, never saved): returns empty payload.
    """
    cred_hash = _hash_credentials(username, pin)
    registry  = _get_registry()

    if cred_hash not in registry:
        return False, "Username or PIN not found. Register first.", None

    entry = registry[cred_hash]
    master_blob_id = entry.get("master_blob_id")

    # New user with no saves yet — return empty state
    if not master_blob_id:
        empty_payload = {
            "schema_version": "2.0",
            "username":    username.strip(),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "previous_blob_id": None,
            "blob_chain":  [],
            "stats":       {"correct": 0, "wrong": 0, "pending": 0, "win_rate": "0%"},
            "predictions": [],
            "grudge_log":  [],
            "hot_takes":   [],
        }
        return True, "new_user", empty_payload

    # Try to load from Walrus
    payload = retrieve_memory(master_blob_id)
    if not payload:
        # Walk blob chain as fallback
        for bid in reversed(entry.get("blob_chain", [])):
            payload = retrieve_memory(bid)
            if payload:
                master_blob_id = bid
                break

    if not payload:
        # Walrus unreachable — still let them in with empty state
        # They can re-save once Walrus recovers
        print(f"[Auth] Warning: could not load Walrus blob for {username}, starting fresh")
        empty_payload = {
            "schema_version": "2.0",
            "username":    username.strip(),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "previous_blob_id": master_blob_id,
            "blob_chain":  entry.get("blob_chain", []),
            "stats":       {"correct": 0, "wrong": 0, "pending": 0, "win_rate": "0%"},
            "predictions": [],
            "grudge_log":  [],
            "hot_takes":   [],
        }
        return True, master_blob_id or "offline", empty_payload

    return True, master_blob_id, payload


def login_by_blob_id(blob_id: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Login directly with a Walrus blob ID — works across sessions/devices.
    No registry lookup needed.
    """
    blob_id = blob_id.strip()
    if not blob_id:
        return False, "Enter a blob ID.", None

    with st.spinner("Loading from Walrus..."):
        payload = retrieve_memory(blob_id)

    if not payload:
        return False, "Could not load that blob ID. Check it's correct and Walrus is reachable.", None

    username = payload.get("username", "unknown")

    # Register this user in session registry so PIN login works too
    # Use blob_id as a stand-in key (no PIN for blob login)
    registry = _get_registry()
    blob_key = f"__blob__{blob_id[:16]}"
    registry[blob_key] = {
        "username":       username,
        "master_blob_id": blob_id,
        "created":        datetime.utcnow().isoformat() + "Z",
        "blob_chain":     payload.get("blob_chain", [blob_id]),
    }
    _save_registry(registry)

    return True, blob_id, payload


def update_user_blob(username: str, pin: str, new_blob_id: str):
    """Update master blob ID after a successful Walrus save."""
    cred_hash = _hash_credentials(username, pin)
    registry  = _get_registry()

    if cred_hash not in registry:
        return

    registry[cred_hash]["master_blob_id"] = new_blob_id
    chain = registry[cred_hash].get("blob_chain", [])
    if new_blob_id not in chain:
        chain.append(new_blob_id)
    registry[cred_hash]["blob_chain"] = chain[-20:]
    _save_registry(registry)
    print(f"[Auth] Updated blob for {username}: {new_blob_id}")


def get_all_users() -> list:
    registry = _get_registry()
    return [v["username"] for v in registry.values()
            if not v["username"].startswith("__blob__")]

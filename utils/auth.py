"""
Auth Module v4 — GitHub Gist as persistent registry.

Architecture:
- Registry (username→PIN_hash→blob_id) stored in a private GitHub Gist as JSON.
- Gist is read on every login/register, written on every change.
- Survives page refreshes, redeploys, and multiple users/devices.
- Requires GITHUB_PAT and GIST_ID in Streamlit secrets or env vars.
- User prediction DATA still lives on Walrus — only the credential
  lookup table lives in the Gist.

Setup (one-time):
  1. Create a private Gist at gist.github.com with filename registry.json
     and content: {}
  2. Copy the Gist ID from the URL (the long hex string).
  3. Add to Streamlit secrets:
       GITHUB_PAT = "ghp_your_token_here"
       GIST_ID    = "your_gist_id_here"
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Optional, Tuple

import requests
import streamlit as st

from utils.walrus_memory import retrieve_memory


# ── GitHub Gist helpers ───────────────────────────────────────────────────────

def _read_secret(key: str, default: str = "") -> str:
    try:
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.environ.get(key, default)


def _gist_headers() -> dict:
    pat = _read_secret("GITHUB_PAT")
    return {
        "Authorization": f"token {pat}",
        "Accept": "application/vnd.github.v3+json",
    }


def _gist_configured() -> bool:
    return bool(_read_secret("GITHUB_PAT") and _read_secret("GIST_ID"))


def _load_gist_registry() -> dict:
    """Fetch registry JSON from GitHub Gist. Falls back to session_state cache."""
    gist_id = _read_secret("GIST_ID")
    if not gist_id:
        return _get_session_registry()
    try:
        r = requests.get(
            f"https://api.github.com/gists/{gist_id}",
            headers=_gist_headers(),
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            files = data.get("files", {})
            # Get registry.json content (or first file)
            content = None
            if "registry.json" in files:
                content = files["registry.json"].get("content", "{}")
            elif files:
                content = list(files.values())[0].get("content", "{}")
            if content:
                registry = json.loads(content)
                # Cache in session state for fast repeat reads
                st.session_state["_gist_registry_cache"] = registry
                return registry
        print(f"[Auth] Gist load failed: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"[Auth] Gist load exception: {e}")
    # Fallback to cached session state
    return st.session_state.get("_gist_registry_cache",
                                _get_session_registry())


def _save_gist_registry(registry: dict) -> bool:
    """Write registry JSON back to GitHub Gist."""
    gist_id = _read_secret("GIST_ID")
    if not gist_id:
        # No Gist configured — fall back to session state only
        _save_session_registry(registry)
        return False
    try:
        payload = {
            "files": {
                "registry.json": {
                    "content": json.dumps(registry, indent=2)
                }
            }
        }
        r = requests.patch(
            f"https://api.github.com/gists/{gist_id}",
            headers=_gist_headers(),
            json=payload,
            timeout=10,
        )
        if r.status_code == 200:
            # Update session cache too
            st.session_state["_gist_registry_cache"] = registry
            _save_session_registry(registry)
            return True
        print(f"[Auth] Gist save failed: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"[Auth] Gist save exception: {e}")
    # Fallback — at least save to session state
    _save_session_registry(registry)
    return False


# ── Session state fallback ────────────────────────────────────────────────────

def _get_session_registry() -> dict:
    if "_auth_registry" not in st.session_state:
        st.session_state["_auth_registry"] = {}
    return st.session_state["_auth_registry"]


def _save_session_registry(registry: dict):
    st.session_state["_auth_registry"] = registry


# ── Credential helpers ────────────────────────────────────────────────────────

def _hash_credentials(username: str, pin: str) -> str:
    raw = f"{username.strip().lower()}:{pin.strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# ── Public API ────────────────────────────────────────────────────────────────

def register_user(username: str, pin: str) -> Tuple[bool, str]:
    """
    Register a new user.
    Writes to GitHub Gist for persistence across sessions.
    Returns (success, message).
    """
    if len(pin) != 4 or not pin.isdigit():
        return False, "PIN must be exactly 4 digits."
    if len(username.strip()) < 2:
        return False, "Username must be at least 2 characters."

    cred_hash = _hash_credentials(username, pin)
    registry  = _load_gist_registry()

    # Check if username already taken (check display names)
    for v in registry.values():
        if v.get("username", "").lower() == username.strip().lower():
            return False, "Username already taken. Try a different one."

    registry[cred_hash] = {
        "username":       username.strip(),
        "master_blob_id": None,
        "created":        datetime.utcnow().isoformat() + "Z",
        "blob_chain":     [],
    }

    saved = _save_gist_registry(registry)
    if not saved and _gist_configured():
        print(f"[Auth] Warning: Gist save failed for {username}, stored in session only")

    print(f"[Auth] Registered: {username.strip()} (gist={saved})")
    return True, "ok"


def login_user(username: str, pin: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Login with username + PIN.
    Loads registry from Gist so credentials persist across refreshes.
    Returns (success, message_or_blob_id, payload_or_None).
    """
    cred_hash = _hash_credentials(username, pin)
    registry  = _load_gist_registry()

    if cred_hash not in registry:
        return False, "Username or PIN not found. Please register first.", None

    entry          = registry[cred_hash]
    master_blob_id = entry.get("master_blob_id")

    # New user — no Walrus data yet
    if not master_blob_id:
        return True, "new_user", _empty_payload(username)

    # Try loading Walrus data
    payload = retrieve_memory(master_blob_id)
    if not payload:
        for bid in reversed(entry.get("blob_chain", [])):
            payload = retrieve_memory(bid)
            if payload:
                master_blob_id = bid
                break

    if not payload:
        print(f"[Auth] Walrus unreachable for {username}, starting fresh")
        return True, master_blob_id or "offline", _empty_payload(username)

    return True, master_blob_id, payload


def login_by_blob_id(blob_id: str) -> Tuple[bool, str, Optional[dict]]:
    """Login directly with a Walrus blob ID — works across any session/device."""
    blob_id = blob_id.strip()
    if not blob_id:
        return False, "Enter a blob ID.", None

    payload = retrieve_memory(blob_id)
    if not payload:
        return False, "Could not load that blob. Check it's correct.", None

    username = payload.get("username", "unknown")
    print(f"[Auth] Blob ID login: {username}")
    return True, blob_id, payload


def update_user_blob(username: str, pin: str, new_blob_id: str):
    """Update master blob ID in Gist after a successful Walrus save."""
    cred_hash = _hash_credentials(username, pin)
    registry  = _load_gist_registry()

    if cred_hash not in registry:
        return

    registry[cred_hash]["master_blob_id"] = new_blob_id
    chain = registry[cred_hash].get("blob_chain", [])
    if new_blob_id not in chain:
        chain.append(new_blob_id)
    registry[cred_hash]["blob_chain"] = chain[-20:]

    _save_gist_registry(registry)
    print(f"[Auth] Blob updated in Gist for {username}: {new_blob_id}")


def get_all_users() -> list:
    registry = _load_gist_registry()
    return [v["username"] for v in registry.values()]


def is_gist_configured() -> bool:
    return _gist_configured()


# ── Internal ──────────────────────────────────────────────────────────────────

def _empty_payload(username: str) -> dict:
    return {
        "schema_version":   "2.0",
        "username":         username.strip(),
        "last_updated":     datetime.utcnow().isoformat() + "Z",
        "previous_blob_id": None,
        "blob_chain":       [],
        "stats":            {"correct": 0, "wrong": 0,
                             "pending": 0, "win_rate": "0%"},
        "predictions":      [],
        "grudge_log":       [],
        "hot_takes":        [],
    }

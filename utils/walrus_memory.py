"""
Walrus Memory Module v3
- Network read at CALL TIME (not import time) so Streamlit secrets work
- Testnet: PUT to public publisher
- Mainnet: tries community publishers in order (PUT), falls back to upload relay (POST)
- WALRUS_EPOCHS env var controls storage duration (default 5)
"""

import json
import os
import requests
from typing import Optional

# ── Endpoints ──────────────────────────────────────────────────────────────────
TESTNET_PUBLISHER  = "https://publisher.walrus-testnet.walrus.space"
TESTNET_AGGREGATOR = "https://aggregator.walrus-testnet.walrus.space"
TESTNET_EXPLORER   = "https://walruscan.com/testnet/blob"

# Community mainnet publishers (PUT /v1/blobs) — tried in order
MAINNET_PUBLISHERS = [
    "https://publisher.walrus.space",          # community
    "https://walrus-publisher.staketab.org",    # community
    "https://walrus.publisher.stakin.com",      # community
]
MAINNET_UPLOAD_RELAY = "https://upload-relay.mainnet.walrus.space"
MAINNET_AGGREGATOR   = "https://aggregator.walrus-mainnet.walrus.space"
MAINNET_EXPLORER     = "https://walruscan.com/mainnet/blob"


def _network() -> str:
    """Read network at call time so Streamlit secrets are always current."""
    # Check st.secrets first (Streamlit Cloud), then env var
    try:
        import streamlit as st
        val = st.secrets.get("WALRUS_NETWORK", "")
        if val:
            return val.lower()
    except Exception:
        pass
    return os.environ.get("WALRUS_NETWORK", "testnet").lower()


def _epochs() -> int:
    try:
        import streamlit as st
        val = st.secrets.get("WALRUS_EPOCHS", "")
        if val:
            return int(val)
    except Exception:
        pass
    return int(os.environ.get("WALRUS_EPOCHS", "5"))


def _extract_blob_id(result: dict) -> Optional[str]:
    if "newlyCreated" in result:
        return result["newlyCreated"]["blobObject"]["blobId"]
    if "alreadyCertified" in result:
        return result["alreadyCertified"]["blobId"]
    return result.get("blobId") or result.get("blob_id") or result.get("id")


def _try_put(url: str, payload: bytes, epochs: int) -> Optional[str]:
    """Attempt a PUT store. Returns blob_id or None."""
    try:
        r = requests.put(
            f"{url}/v1/blobs?epochs={epochs}",
            data=payload,
            headers={"Content-Type": "application/octet-stream"},
            timeout=20,
        )
        if r.status_code in (200, 201):
            return _extract_blob_id(r.json())
        print(f"[Walrus] PUT {url} → {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[Walrus] PUT {url} exception: {e}")
    return None


def _try_post_relay(payload: bytes, epochs: int) -> Optional[str]:
    """Attempt a POST to the mainnet upload relay."""
    try:
        r = requests.post(
            f"{MAINNET_UPLOAD_RELAY}/v1/blob-upload-relay?epochs={epochs}",
            data=payload,
            headers={"Content-Type": "application/octet-stream"},
            timeout=20,
        )
        if r.status_code in (200, 201):
            return _extract_blob_id(r.json())
        print(f"[Walrus] Relay POST → {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[Walrus] Relay POST exception: {e}")
    return None


def store_memory(data: dict) -> Optional[str]:
    """Store JSON payload on Walrus. Returns blob_id or None."""
    network = _network()
    epochs  = _epochs()
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")

    if network == "mainnet":
        # Try community publishers first
        for pub in MAINNET_PUBLISHERS:
            blob_id = _try_put(pub, payload, epochs)
            if blob_id:
                print(f"[Walrus:mainnet] Stored via {pub}")
                return blob_id
        # Fallback: upload relay (POST)
        blob_id = _try_post_relay(payload, epochs)
        if blob_id:
            print(f"[Walrus:mainnet] Stored via upload relay")
        return blob_id
    else:
        # Testnet
        return _try_put(TESTNET_PUBLISHER, payload, epochs)


def retrieve_memory(blob_id: str) -> Optional[dict]:
    """Retrieve and decode a JSON blob from Walrus by blob_id."""
    network = _network()
    aggregator = MAINNET_AGGREGATOR if network == "mainnet" else TESTNET_AGGREGATOR
    try:
        r = requests.get(f"{aggregator}/v1/blobs/{blob_id}", timeout=30)
        if r.status_code == 200:
            return json.loads(r.content.decode("utf-8"))
        print(f"[Walrus:{network}] Retrieve failed: {r.status_code}")
        return None
    except Exception as e:
        print(f"[Walrus:{network}] Retrieve exception: {e}")
        return None


def get_walrus_explorer_url(blob_id: str) -> str:
    network = _network()
    base = MAINNET_EXPLORER if network == "mainnet" else TESTNET_EXPLORER
    return f"{base}/{blob_id}"


def get_network_name() -> str:
    return _network().upper()

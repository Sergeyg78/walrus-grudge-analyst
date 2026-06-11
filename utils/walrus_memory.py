"""
Walrus Memory Module v4
- Uses st.secrets["KEY"] with proper KeyError handling (not .get())
- Testnet: PUT to public publisher
- Mainnet: tries community publishers, falls back to upload relay
"""

import json
import os
import requests
from typing import Optional

TESTNET_PUBLISHER  = "https://publisher.walrus-testnet.walrus.space"
TESTNET_AGGREGATOR = "https://aggregator.walrus-testnet.walrus.space"
TESTNET_EXPLORER   = "https://walruscan.com/testnet/blob"

MAINNET_PUBLISHERS = [
    "https://publisher.walrus.space",
    "https://walrus-publisher.staketab.org",
    "https://walrus.publisher.stakin.com",
]
MAINNET_UPLOAD_RELAY = "https://upload-relay.mainnet.walrus.space"
MAINNET_AGGREGATOR   = "https://aggregator.walrus-mainnet.walrus.space"
MAINNET_EXPLORER     = "https://walruscan.com/mainnet/blob"


def _read_secret(key: str, default: str = "") -> str:
    """
    Safely read from st.secrets then os.environ.
    st.secrets uses dict-style access — KeyError if missing, not None.
    """
    try:
        import streamlit as st
        # st.secrets behaves like a dict — use 'in' check first
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.environ.get(key, default)


def _network() -> str:
    return _read_secret("WALRUS_NETWORK", "testnet").lower().strip()


def _epochs() -> int:
    return int(_read_secret("WALRUS_EPOCHS", "5"))


def _extract_blob_id(result: dict) -> Optional[str]:
    if "newlyCreated" in result:
        return result["newlyCreated"]["blobObject"]["blobId"]
    if "alreadyCertified" in result:
        return result["alreadyCertified"]["blobId"]
    return result.get("blobId") or result.get("blob_id") or result.get("id")


def _try_put(base_url: str, payload: bytes, epochs: int) -> Optional[str]:
    try:
        r = requests.put(
            f"{base_url}/v1/blobs?epochs={epochs}",
            data=payload,
            headers={"Content-Type": "application/octet-stream"},
            timeout=20,
        )
        if r.status_code in (200, 201):
            return _extract_blob_id(r.json())
        print(f"[Walrus] PUT {base_url} → {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"[Walrus] PUT {base_url} exception: {e}")
    return None


def _try_post_relay(payload: bytes, epochs: int) -> Optional[str]:
    try:
        r = requests.post(
            f"{MAINNET_UPLOAD_RELAY}/v1/blob-upload-relay?epochs={epochs}",
            data=payload,
            headers={"Content-Type": "application/octet-stream"},
            timeout=20,
        )
        if r.status_code in (200, 201):
            return _extract_blob_id(r.json())
        print(f"[Walrus] Relay POST → {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"[Walrus] Relay POST exception: {e}")
    return None


def store_memory(data: dict) -> Optional[str]:
    network = _network()
    epochs  = _epochs()
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")

    print(f"[Walrus] store_memory called. network={network} epochs={epochs}")

    if network == "mainnet":
        for pub in MAINNET_PUBLISHERS:
            blob_id = _try_put(pub, payload, epochs)
            if blob_id:
                print(f"[Walrus:mainnet] Stored via {pub} → {blob_id}")
                return blob_id
        blob_id = _try_post_relay(payload, epochs)
        if blob_id:
            print(f"[Walrus:mainnet] Stored via relay → {blob_id}")
        return blob_id
    else:
        blob_id = _try_put(TESTNET_PUBLISHER, payload, epochs)
        if blob_id:
            print(f"[Walrus:testnet] Stored → {blob_id}")
        return blob_id


def retrieve_memory(blob_id: str) -> Optional[dict]:
    network    = _network()
    aggregator = MAINNET_AGGREGATOR if network == "mainnet" else TESTNET_AGGREGATOR
    try:
        r = requests.get(f"{aggregator}/v1/blobs/{blob_id}", timeout=30)
        if r.status_code == 200:
            return json.loads(r.content.decode("utf-8"))
        print(f"[Walrus:{network}] Retrieve {blob_id} → {r.status_code}")
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

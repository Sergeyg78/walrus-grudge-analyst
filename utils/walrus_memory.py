"""
Walrus Memory Module
Handles storing/retrieving blobs on Walrus testnet or mainnet.

MAINNET NOTES (confirmed via live testing 2026-06-10):
- No public unauthenticated publisher on mainnet.
- Upload relay at upload-relay.mainnet.walrus.space uses POST (not PUT).
  Confirmed: PUT returns HTTP 405, allow: POST.
- Reads use the public mainnet aggregator — free, no auth needed.
- Switch via WALRUS_NETWORK env var: "testnet" (default) or "mainnet"
- Set storage duration via WALRUS_EPOCHS env var (default: 5)
  Testnet epoch = 1 day | Mainnet epoch = 2 weeks
  So WALRUS_EPOCHS=5 on mainnet = ~10 weeks of storage
"""

import json
import os
import requests
from typing import Optional

NETWORK = os.environ.get("WALRUS_NETWORK", "testnet").lower()
EPOCHS  = int(os.environ.get("WALRUS_EPOCHS", "5"))

ENDPOINTS = {
    "testnet": {
        "publisher":  "https://publisher.walrus-testnet.walrus.space",
        "pub_path":   "/v1/blobs",
        "pub_method": "PUT",   # testnet publisher: PUT
        "aggregator": "https://aggregator.walrus-testnet.walrus.space",
        "explorer":   "https://walruscan.com/testnet/blob",
    },
    "mainnet": {
        # Mysten Labs upload relay — POST confirmed, handles WAL payment
        "publisher":  "https://upload-relay.mainnet.walrus.space",
        "pub_path":   "/v1/blob-upload-relay",
        "pub_method": "POST",  # mainnet upload relay: POST
        # Public mainnet aggregator — free reads, no auth
        "aggregator": "https://aggregator.walrus-mainnet.walrus.space",
        "explorer":   "https://walruscan.com/mainnet/blob",
    },
}


def _cfg() -> dict:
    return ENDPOINTS.get(NETWORK, ENDPOINTS["testnet"])


def _extract_blob_id(result: dict) -> Optional[str]:
    """Extract blob ID from any known Walrus response shape."""
    if "newlyCreated" in result:
        return result["newlyCreated"]["blobObject"]["blobId"]
    if "alreadyCertified" in result:
        return result["alreadyCertified"]["blobId"]
    # Upload relay flat format
    return result.get("blobId") or result.get("blob_id") or result.get("id")


def store_memory(data: dict) -> Optional[str]:
    """
    Store a JSON payload on Walrus.
    Uses PUT on testnet, POST on mainnet (upload relay).
    Returns blob_id on success, None on failure.
    """
    try:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        cfg    = _cfg()
        url    = f"{cfg['publisher']}{cfg['pub_path']}?epochs={EPOCHS}"
        method = cfg["pub_method"]
        headers = {"Content-Type": "application/octet-stream"}

        response = (
            requests.post(url, data=payload, headers=headers, timeout=30)
            if method == "POST"
            else requests.put(url, data=payload, headers=headers, timeout=30)
        )

        if response.status_code in (200, 201):
            return _extract_blob_id(response.json())

        print(f"[Walrus:{NETWORK}] Store failed {method} → "
              f"{response.status_code}: {response.text[:300]}")
        return None
    except Exception as e:
        print(f"[Walrus:{NETWORK}] Store exception: {e}")
        return None


def retrieve_memory(blob_id: str) -> Optional[dict]:
    """Retrieve and decode a JSON blob from Walrus by blob_id."""
    try:
        url = f"{_cfg()['aggregator']}/v1/blobs/{blob_id}"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return json.loads(response.content.decode("utf-8"))
        print(f"[Walrus:{NETWORK}] Retrieve failed: {response.status_code}")
        return None
    except Exception as e:
        print(f"[Walrus:{NETWORK}] Retrieve exception: {e}")
        return None


def get_walrus_explorer_url(blob_id: str) -> str:
    return f"{_cfg()['explorer']}/{blob_id}"


def get_network_name() -> str:
    return NETWORK.upper()

"""
Walrus Memory Module
Handles storing/retrieving blobs on Walrus testnet or mainnet.
Switch via WALRUS_NETWORK env var: "testnet" (default) or "mainnet"
"""

import json
import os
import requests
from datetime import datetime
from typing import Optional

# ── Network config ─────────────────────────────────────────────────────────────
NETWORK = os.environ.get("WALRUS_NETWORK", "testnet").lower()

ENDPOINTS = {
    "testnet": {
        "publisher":  "https://publisher.walrus-testnet.walrus.space",
        "aggregator": "https://aggregator.walrus-testnet.walrus.space",
        "explorer":   "https://walruscan.com/testnet/blob",
    },
    "mainnet": {
        "publisher":  "https://publisher.walrus.space",
        "aggregator": "https://aggregator.walrus.space",
        "explorer":   "https://walruscan.com/mainnet/blob",
    },
}

def _cfg():
    return ENDPOINTS.get(NETWORK, ENDPOINTS["testnet"])


def store_memory(data: dict) -> Optional[str]:
    """Store JSON payload on Walrus. Returns blob_id or None."""
    try:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        response = requests.put(
            f"{_cfg()['publisher']}/v1/blobs",
            data=payload,
            headers={"Content-Type": "application/octet-stream"},
            timeout=30,
        )
        if response.status_code in (200, 201):
            result = response.json()
            if "newlyCreated" in result:
                return result["newlyCreated"]["blobObject"]["blobId"]
            elif "alreadyCertified" in result:
                return result["alreadyCertified"]["blobId"]
            return result.get("blobId") or result.get("blob_id")
        print(f"[Walrus] Store failed: {response.status_code} — {response.text[:200]}")
        return None
    except Exception as e:
        print(f"[Walrus] Store exception: {e}")
        return None


def retrieve_memory(blob_id: str) -> Optional[dict]:
    """Retrieve and decode a JSON blob from Walrus by blob_id."""
    try:
        response = requests.get(
            f"{_cfg()['aggregator']}/v1/blobs/{blob_id}",
            timeout=30,
        )
        if response.status_code == 200:
            return json.loads(response.content.decode("utf-8"))
        print(f"[Walrus] Retrieve failed: {response.status_code}")
        return None
    except Exception as e:
        print(f"[Walrus] Retrieve exception: {e}")
        return None


def get_walrus_explorer_url(blob_id: str) -> str:
    return f"{_cfg()['explorer']}/{blob_id}"


def get_network_name() -> str:
    return NETWORK.upper()

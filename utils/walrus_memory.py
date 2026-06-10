"""
Walrus Memory Module
Handles storing/retrieving blobs on Walrus testnet or mainnet.

MAINNET NOTE (from official docs at docs.wal.app):
- There is NO public unauthenticated publisher on mainnet.
- Writes on mainnet go through the Mysten Labs Upload Relay endpoint.
- The upload relay accepts blobs at /v1/blob-upload-relay (not /v1/blobs).
- Reads use the public mainnet aggregator — free, no auth needed.
- Switch via WALRUS_NETWORK env var: "testnet" (default) or "mainnet"
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
        "publisher":     "https://publisher.walrus-testnet.walrus.space",
        "pub_path":      "/v1/blobs",
        "aggregator":    "https://aggregator.walrus-testnet.walrus.space",
        "explorer":      "https://walruscan.com/testnet/blob",
    },
    "mainnet": {
        # Official Mysten Labs upload relay — handles WAL payment server-side
        # Source: https://docs.wal.app/docs/network-reference
        "publisher":     "https://upload-relay.mainnet.walrus.space",
        "pub_path":      "/v1/blob-upload-relay",
        # Public mainnet aggregator — free, no auth needed
        "aggregator":    "https://aggregator.walrus-mainnet.walrus.space",
        "explorer":      "https://walruscan.com/mainnet/blob",
    },
}


def _cfg():
    return ENDPOINTS.get(NETWORK, ENDPOINTS["testnet"])


def store_memory(data: dict) -> Optional[str]:
    """Store JSON payload on Walrus. Returns blob_id or None."""
    try:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        cfg = _cfg()
        url = f"{cfg['publisher']}{cfg['pub_path']}"

        response = requests.put(
            url,
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
            # Upload relay may return differently
            return (
                result.get("blobId")
                or result.get("blob_id")
                or result.get("newlyCreated", {}).get("blobObject", {}).get("blobId")
            )
        print(f"[Walrus] Store failed: {response.status_code} — {response.text[:300]}")
        return None
    except Exception as e:
        print(f"[Walrus] Store exception: {e}")
        return None


def retrieve_memory(blob_id: str) -> Optional[dict]:
    """Retrieve and decode a JSON blob from Walrus by blob_id."""
    try:
        url = f"{_cfg()['aggregator']}/v1/blobs/{blob_id}"
        response = requests.get(url, timeout=30)
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

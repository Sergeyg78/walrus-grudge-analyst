"""
Walrus Testnet Memory Module
Handles storing and retrieving prediction memory as blobs on Walrus testnet.
"""

import json
import requests
import time
from datetime import datetime
from typing import Optional

# Walrus Testnet endpoints
WALRUS_PUBLISHER = "https://publisher.walrus-testnet.walrus.space"
WALRUS_AGGREGATOR = "https://aggregator.walrus-testnet.walrus.space"

HEADERS = {"Content-Type": "application/json"}


def store_memory(data: dict) -> Optional[str]:
    """
    Store a JSON payload on Walrus testnet.
    Returns the blob_id on success, None on failure.
    """
    try:
        payload = json.dumps(data, ensure_ascii=False)
        response = requests.put(
            f"{WALRUS_PUBLISHER}/v1/blobs",
            data=payload.encode("utf-8"),
            headers={"Content-Type": "application/octet-stream"},
            timeout=30,
        )
        if response.status_code in (200, 201):
            result = response.json()
            # Handle both newlyCreated and alreadyCertified responses
            if "newlyCreated" in result:
                blob_id = result["newlyCreated"]["blobObject"]["blobId"]
            elif "alreadyCertified" in result:
                blob_id = result["alreadyCertified"]["blobId"]
            else:
                blob_id = result.get("blobId") or result.get("blob_id")
            return blob_id
        else:
            print(f"[Walrus] Store failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[Walrus] Store exception: {e}")
        return None


def retrieve_memory(blob_id: str) -> Optional[dict]:
    """
    Retrieve and decode a JSON blob from Walrus testnet by blob_id.
    Returns parsed dict on success, None on failure.
    """
    try:
        response = requests.get(
            f"{WALRUS_AGGREGATOR}/v1/blobs/{blob_id}",
            timeout=30,
        )
        if response.status_code == 200:
            return json.loads(response.content.decode("utf-8"))
        else:
            print(f"[Walrus] Retrieve failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[Walrus] Retrieve exception: {e}")
        return None


def build_memory_snapshot(
    username: str,
    predictions: list,
    grudge_log: list,
    stats: dict,
    existing_blob_id: Optional[str] = None,
) -> dict:
    """
    Build a full memory snapshot dict ready to be stored on Walrus.
    """
    return {
        "schema_version": "1.0",
        "username": username,
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "previous_blob_id": existing_blob_id,
        "stats": stats,
        "predictions": predictions,
        "grudge_log": grudge_log,
    }


def get_walrus_explorer_url(blob_id: str) -> str:
    """Return a Walrus testnet explorer URL for a blob."""
    return f"https://walruscan.com/testnet/blob/{blob_id}"

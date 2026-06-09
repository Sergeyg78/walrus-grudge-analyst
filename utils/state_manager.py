"""
State Manager v2
Handles in-app state with blob chain support and auto-save triggers.
"""

from datetime import datetime
from typing import Optional


def empty_state(username: str) -> dict:
    return {
        "username":   username,
        "blob_id":    None,
        "blob_chain": [],
        "predictions": [],
        "grudge_log":  [],
        "hot_takes":   [],
        "stats": {
            "correct": 0, "wrong": 0, "pending": 0, "win_rate": "0%"
        },
    }


def add_prediction(state: dict, match: str, prediction: str) -> dict:
    state["predictions"].append({
        "id":         len(state["predictions"]) + 1,
        "match":      match,
        "prediction": prediction,
        "result":     None,
        "status":     "pending",
        "date":       datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "roast":      None,
    })
    state["stats"]["pending"] += 1
    return state


def resolve_prediction(state: dict, pred_id: int, actual_result: str, correct: bool) -> dict:
    for p in state["predictions"]:
        if p["id"] == pred_id and p["status"] == "pending":
            p["result"]        = actual_result
            p["status"]        = "correct" if correct else "wrong"
            p["resolved_date"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            state["stats"]["pending"] = max(0, state["stats"]["pending"] - 1)
            if correct:
                state["stats"]["correct"] += 1
            else:
                state["stats"]["wrong"] += 1
                state["grudge_log"].append({
                    "prediction_id": pred_id,
                    "match":         p["match"],
                    "prediction":    p["prediction"],
                    "actual":        actual_result,
                    "date":          p.get("date", "unknown"),
                })
            break

    total = state["stats"]["correct"] + state["stats"]["wrong"]
    if total > 0:
        pct = round((state["stats"]["correct"] / total) * 100)
        state["stats"]["win_rate"] = f"{pct}%"
    return state


def add_hot_take(state: dict, take: str) -> dict:
    state["hot_takes"].append({
        "take": take,
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    })
    return state


def get_pending_predictions(state: dict) -> list:
    return [p for p in state["predictions"] if p["status"] == "pending"]


def get_resolved_predictions(state: dict) -> list:
    return [p for p in state["predictions"] if p["status"] != "pending"]


def state_to_walrus_payload(state: dict) -> dict:
    return {
        "schema_version":   "2.0",
        "username":         state["username"],
        "last_updated":     datetime.utcnow().isoformat() + "Z",
        "previous_blob_id": state.get("blob_id"),
        "blob_chain":       state.get("blob_chain", []),
        "stats":            state["stats"],
        "predictions":      state["predictions"],
        "grudge_log":       state["grudge_log"],
        "hot_takes":        state["hot_takes"],
    }


def walrus_payload_to_state(payload: dict) -> dict:
    return {
        "username":    payload.get("username", "unknown"),
        "blob_id":     None,
        "blob_chain":  payload.get("blob_chain", []),
        "predictions": payload.get("predictions", []),
        "grudge_log":  payload.get("grudge_log", []),
        "hot_takes":   payload.get("hot_takes", []),
        "stats":       payload.get("stats", {
            "correct": 0, "wrong": 0, "pending": 0, "win_rate": "0%"
        }),
    }

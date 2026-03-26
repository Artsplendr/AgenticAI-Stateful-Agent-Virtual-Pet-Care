# This file saves agent state → data/state.json, loads state on startup, handles first-time initialization, converts between Pydantic ↔ JSON

import json
import os
from datetime import datetime
from typing import Any, Dict, Union

from app.graph.state import PetState, Interaction

DATA_PATH = "data/state.json"


def ensure_data_dir():
    os.makedirs("data", exist_ok=True)


def normalize_state(state: Union[PetState, Dict[str, Any]]) -> PetState:
    """
    Coerce graph output into PetState.
    LangGraph can return either a model instance or a plain dict.
    """
    if isinstance(state, PetState):
        return state

    if not isinstance(state, dict):
        raise TypeError(f"Unsupported state type: {type(state)!r}")

    data = dict(state)

    # Restore datetime-like fields if they are serialized strings.
    for key in ("last_interaction_time", "last_updated"):
        value = data.get(key)
        if isinstance(value, str):
            data[key] = datetime.fromisoformat(value)

    # Restore interaction history into Interaction models.
    restored_history = []
    for item in data.get("interaction_history", []):
        if isinstance(item, Interaction):
            restored_history.append(item)
            continue

        if isinstance(item, dict):
            timestamp = item.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            elif not isinstance(timestamp, datetime):
                timestamp = datetime.utcnow()

            restored_history.append(
                Interaction(
                    timestamp=timestamp,
                    type=item.get("type", "agent_message"),
                    content=item.get("content", ""),
                )
            )

    data["interaction_history"] = restored_history
    return PetState(**data)


def serialize_state(state: PetState) -> dict:
    """
    Convert Pydantic state into JSON-serializable dict.
    """

    data = state.model_dump() if hasattr(state, "model_dump") else state.dict()

    # Convert datetime fields to ISO format
    if state.last_interaction_time:
        data["last_interaction_time"] = state.last_interaction_time.isoformat()

    data["last_updated"] = state.last_updated.isoformat()

    # Serialize interaction history
    serialized_history = []
    for item in state.interaction_history:
        serialized_history.append({
            "timestamp": item.timestamp.isoformat(),
            "type": item.type,
            "content": item.content
        })

    data["interaction_history"] = serialized_history

    return data


def deserialize_state(data: dict) -> PetState:
    """
    Convert JSON dict back into PetState.
    """

    # Restore datetime fields
    if data.get("last_interaction_time"):
        data["last_interaction_time"] = datetime.fromisoformat(data["last_interaction_time"])

    if data.get("last_updated"):
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])

    # Restore interaction history
    history = []
    for item in data.get("interaction_history", []):
        history.append(Interaction(
            timestamp=datetime.fromisoformat(item["timestamp"]),
            type=item["type"],
            content=item["content"]
        ))

    data["interaction_history"] = history

    return PetState(**data)


def load_state() -> PetState:
    """
    Load state from file or initialize new one.
    """

    ensure_data_dir()

    if not os.path.exists(DATA_PATH):
        print("🆕 No previous state found. Initializing new state.")
        return PetState()

    try:
        with open(DATA_PATH, "r") as f:
            data = json.load(f)

        state = deserialize_state(data)
        print("✅ Loaded existing state.")
        return state

    except Exception as e:
        print(f"⚠️ Failed to load state, creating new one. Error: {e}")
        return PetState()


def save_state(state: Union[PetState, Dict[str, Any]]):
    """
    Save current state to file.
    """

    ensure_data_dir()
    state = normalize_state(state)

    data = serialize_state(state)

    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print("💾 State saved.")
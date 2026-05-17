"""
utils/session_store.py
─────────────────────
Lightweight file-based session store shared across sub-agent servers.
Allows data_collector → risk_assessor → report_generator data flow
WITHOUT passing large JSON through the orchestrator's LLM context.
"""
import json
import os

SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)


def save(session_id: str, key: str, data) -> str:
    """Save data for a session key. Returns the file path."""
    path = os.path.join(SESSION_DIR, f"{session_id}_{key}.json")
    with open(path, "w") as f:
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f)
    return path


def load(session_id: str, key: str):
    """Load data for a session key. Returns parsed dict or raw string."""
    path = os.path.join(SESSION_DIR, f"{session_id}_{key}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        content = f.read()
    try:
        return json.loads(content)
    except Exception:
        return content


def exists(session_id: str, key: str) -> bool:
    path = os.path.join(SESSION_DIR, f"{session_id}_{key}.json")
    return os.path.exists(path)

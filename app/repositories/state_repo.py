from app.core.redis_client import r
import json

def get_state(chat_id: int) -> dict | None:
    data = r.get(f"user:{chat_id}")
    return json.loads(data) if data else None

def set_state(chat_id: int, state: dict) -> None:
    r.set(f"user:{chat_id}", json.dumps(state))

def delete_state(chat_id: int) -> None:
    r.delete(f"user:{chat_id}")
from app.core.redis_client import r
import json

def get_state(chat_id):
    data = r.get(f"user:{chat_id}")
    return json.loads(data) if data else None

def set_state(chat_id, state):
    r.set(f"user:{chat_id}", json.dumps(state))

def delete_state(chat_id):
    r.delete(f"user:{chat_id}")
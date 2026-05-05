import json
import os

FILE = "data/users.json"

def _load():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def has_consent(chat_id):
    users = _load()
    return users.get(str(chat_id), {}).get("consent", False)

def give_consent(chat_id):
    users = _load()
    users[str(chat_id)] = {"consent": True}
    _save(users)
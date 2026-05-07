
#=========Consent===========

from app.core.db import get_cursor

def has_consent(chat_id):
    cur = get_cursor()
    cur.execute("SELECT 1 FROM users WHERE chat_id=%s", (chat_id,))
    return cur.fetchone() is not None

def give_consent(chat_id):
    cur = get_cursor()
    cur.execute(
        "INSERT INTO users (chat_id) VALUES (%s) ON CONFLICT DO NOTHING",
        (chat_id,)
    )
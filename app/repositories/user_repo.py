
#=========Consent===========

from app.core.db import (
    get_cursor
)

from app.core.logger import (
    logger
)

def has_consent(chat_id: int) -> bool:
    cur = get_cursor()
    cur.execute("SELECT 1 FROM users WHERE chat_id=%s", (chat_id,))
    result = cur.fetchone()
    logger.info(

        f"Checked consent for chat_id: {chat_id}, result: {'Yes' if result else 'No'}",

        extra={
            "chat_id": chat_id, 
            "result": result
        }
    )
    return result is not None

def give_consent(chat_id: int) -> None:
    cur = get_cursor()
    cur.execute(
        "INSERT INTO users (chat_id) VALUES (%s) ON CONFLICT DO NOTHING",
        (chat_id,)
    )
    logger.info(

        f"Consent given for chat_id: {chat_id}",

        extra={
            "chat_id": chat_id
        }
    )
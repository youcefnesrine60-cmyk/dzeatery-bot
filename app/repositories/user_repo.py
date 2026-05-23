#=========Consent===========

from app.core.db import (
    get_cursor,
    commit
)

from app.core.logger import (
    logger
)

# ==========================================
# ✅ CHECK CONSENT
# ==========================================

def has_consent(chat_id: int) -> bool:

    cur = get_cursor()

    cur.execute(
        "SELECT 1 FROM users WHERE chat_id=%s",
        (chat_id,)
    )

    result = cur.fetchone()

    logger.info(

        f"Checked consent for chat_id: {chat_id}",

        extra={
            "chat_id": chat_id,
            "has_consent": result is not None
        }
    )

    return result is not None


# ==========================================
# ✅ GIVE CONSENT
# ==========================================

def give_consent(chat_id: int) -> None:

    cur = get_cursor()

    cur.execute(

        """
        INSERT INTO users (chat_id, consent)
        VALUES (%s, TRUE)
        ON CONFLICT (chat_id)
        DO NOTHING
        """,

        (chat_id,)
    )

    # ======================================
    # 💾 SAVE CHANGES
    # ======================================

    commit()

    logger.info(

        f"Consent given for chat_id: {chat_id}",

        extra={
            "chat_id": chat_id
        }
    )
# ========================================
# ✅ CONSENT REPOSITORY
# Async Psycopg3 Version
# ==========================================

from app.core.db import (
    execute, 
    fetchrow
)

from app.core.logger import logger


# ==========================================
# ✅ CHECK CONSENT
# ==========================================

async def has_consent(
    *,
    chat_id: int
) -> bool:

    row = await fetchrow(
        """
        SELECT 1
        FROM users
        WHERE chat_id = %s
          AND consent = TRUE
        LIMIT 1
        """,
        chat_id,
    )

    result = row is not None

    logger.info(
        "checked_consent",
        extra={
            "chat_id": chat_id,
            "has_consent": result,
        },
    )

    return result


# ==========================================
# ✅ GIVE CONSENT
# ==========================================

async def give_consent(
    *,
    chat_id: int
) -> None:

    await execute(
        """
        INSERT INTO users (chat_id, consent)
        VALUES (%s, TRUE)
        ON CONFLICT (chat_id)
        DO UPDATE SET consent = TRUE
        """,
        chat_id,
    )

    logger.info(
        "consent_given",
        extra={"chat_id": chat_id},
    )
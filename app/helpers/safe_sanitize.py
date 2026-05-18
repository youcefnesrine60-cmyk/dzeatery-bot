from app.services.sanitize_service import (
    sanitize_text
)

from app.core.logger import (
    logger
)


# ==============================================
# 🧼 SAFE SANITIZE
# ==============================================

def safe_sanitize(

    chat_id: int,

    text: str,

    field: str

) -> str | None:

    try:

        return sanitize_text(text)

    except Exception as e:

        logger.exception(

            "sanitize_failed",

            extra={

                "chat_id": chat_id,

                "field": field,

                "text_length": len(text),

                "error": str(e)
            }
        )

        return None
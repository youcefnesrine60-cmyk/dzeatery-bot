# ==============================================
# 🧼 SANITIZER SERVICE
# ==============================================

import re

from app.core.logger import (
    logger
)

from app.services.validation.text_rules import (
    MAX_NAME_LENGTH,
    MAX_WILAYA_LENGTH,
    MAX_DESCRIPTION_LENGTH
)

# ==============================================
# 🧼 BASE SANITIZER
# ==============================================

def _sanitize(

    *,

    text: str | None,

    pattern: str,

    max_length: int,

    field: str,

    chat_id: int | None = None

) -> str | None:

    # ==========================================
    # 🚫 NONE INPUT
    # ==========================================

    if text is None:

        logger.warning(

            "sanitize_none_input",

            extra={
                "chat_id": chat_id,
                "field": field
            }
        )

        return None

    # ==========================================
    # 🚫 INVALID TYPE
    # ==========================================

    if not isinstance(text, str):

        logger.warning(

            "sanitize_invalid_type",

            extra={
                "chat_id": chat_id,
                "field": field,
                "input_type": str(type(text))
            }
        )

        return None

    try:

        # ======================================
        # 🧹 REMOVE OUTER SPACES
        # ======================================

        text = text.strip()

        # ======================================
        # 🚫 EMPTY AFTER STRIP
        # ======================================

        if not text:

            logger.warning(

                "sanitize_empty_after_strip",

                extra={
                    "chat_id": chat_id,
                    "field": field
                }
            )

            return None

        # ======================================
        # 🧼 REMOVE INVALID CHARACTERS
        # ======================================

        text = re.sub(

            pattern,

            "",

            text
        )

        # ======================================
        # 🧼 NORMALIZE SPACES
        # ======================================

        text = re.sub(

            r"\s+",

            " ",

            text
        )

        # ======================================
        # 📏 LIMIT LENGTH
        # ======================================

        text = text[:max_length]

        # ======================================
        # 🧹 FINAL CLEANUP
        # ======================================

        text = text.strip()

        # ======================================
        # 🚫 TOO SHORT
        # ======================================

        if len(text) < 2:

            logger.warning(

                "sanitize_too_short",

                extra={
                    "chat_id": chat_id,
                    "field": field
                }
            )

            return None

        # ======================================
        # ✅ SUCCESS
        # ======================================

        logger.info(

            "sanitize_success",

            extra={
                "chat_id": chat_id,
                "field": field
            }
        )

        return text

    # ==========================================
    # 🚫 EXCEPTION
    # ==========================================

    except Exception as e:

        logger.exception(

            "sanitize_failed",

            extra={
                "chat_id": chat_id,
                "field": field,
                "error": str(e)
            }
        )

        return None

# ==============================================
# 🍽️ RESTAURANT SANITIZER
# ==============================================

def sanitize_restaurant(

    *,

    text: str | None,

    chat_id: int | None = None

) -> str | None:

    return _sanitize(

        text=text,

        pattern=r"[^a-zA-Z0-9\u0600-\u06FF\s\-&']",

        max_length=MAX_NAME_LENGTH,

        field="restaurant",

        chat_id=chat_id
    )

# ==============================================
# 👤 OWNER SANITIZER
# ==============================================

def sanitize_owner(

    *,

    text: str | None,

    chat_id: int | None = None

) -> str | None:

    return _sanitize(

        text=text,

        pattern=r"[^a-zA-Z\u0600-\u06FF\s\-']",

        max_length=MAX_NAME_LENGTH,

        field="owner",

        chat_id=chat_id
    )

# ==============================================
# 🗺️ WILAYA SANITIZER
# ==============================================

def sanitize_wilaya(

    *,

    text: str | None,

    chat_id: int | None = None

) -> str | None:

    return _sanitize(

        text=text,

        pattern=r"[^a-zA-Z\u0600-\u06FF\s\-]",

        max_length=MAX_WILAYA_LENGTH,

        field="wilaya",

        chat_id=chat_id
    )

# ==============================================
# 📝 DESCRIPTION SANITIZER
# ==============================================

def sanitize_description(

    *,

    text: str | None,

    chat_id: int | None = None

) -> str | None:

    return _sanitize(

        text=text,

        pattern=r"[^a-zA-Z0-9\u0600-\u06FF\s\-\.,!?&':]",

        max_length=MAX_DESCRIPTION_LENGTH,

        field="description",

        chat_id=chat_id
    )
# ==============================================
# 🛡️ SAFE SANITIZER
# ==============================================

from app.services.validation import (

    sanitize_restaurant,
    sanitize_owner,
    sanitize_wilaya,
    sanitize_description
)

from app.core.logger import (
    logger
)

# ==============================================
# 🧼 SANITIZER MAP
# ==============================================

SANITIZERS = {

    "restaurant": sanitize_restaurant,

    "owner": sanitize_owner,

    "wilaya": sanitize_wilaya,

    "description": sanitize_description
}

# ==============================================
# 🧼 SAFE SANITIZE
# ==============================================

def safe_sanitize(

    *,

    chat_id: int,

    text: str,

    field: str

) -> str | None:

    try:

        # ======================================
        # 🔍 GET SANITIZER
        # ======================================

        sanitizer = SANITIZERS.get(field)

        # ======================================
        # 🚫 UNKNOWN FIELD
        # ======================================

        if not sanitizer:

            logger.warning(

                "safe_sanitize_unknown_field",

                extra={
                    "chat_id": chat_id,
                    "field": field
                }
            )

            return None

        # ======================================
        # 🧼 START SANITIZATION
        # ======================================

        logger.info(

            "safe_sanitize_started",

            extra={
                "chat_id": chat_id,
                "field": field
            }
        )

        # ======================================
        # 🧼 SANITIZE
        # ======================================

        clean = sanitizer(

            text = text,

            chat_id = chat_id
        )

        # ======================================
        # 🚫 INVALID INPUT
        # ======================================

        if not clean:
            #=== Dont logger ====
            return None

        # ======================================
        # ✅ SUCCESS
        # ======================================

        logger.info(

            "safe_sanitize_success",

            extra={
                "chat_id": chat_id,
                "field": field
            }
        )

        return clean

    # ==========================================
    # 🚫 EXCEPTION
    # ==========================================

    except Exception as e:

        logger.exception(

            "safe_sanitize_failed",

            extra={
                "chat_id": chat_id,
                "field": field,
                "error": str(e)
            }
        )

        return None
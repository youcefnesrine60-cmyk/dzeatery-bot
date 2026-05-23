# ==============================================
# 🛡️ SAFE SANITIZER
# ==============================================

from app.services.validation import (
    sanitize_restaurant_name,
    sanitize_owner_name,
    sanitize_wilaya,
    sanitize_description
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

        # ======================================
        # 🍽️ RESTAURANT
        # ======================================

        if field == "restaurant":

            return sanitize_restaurant_name(

                text,

                chat_id
            )

        # ======================================
        # 👤 OWNER
        # ======================================

        if field == "owner":

            return sanitize_owner_name(

                text,

                chat_id
            )

        # ======================================
        # 🗺️ WILAYA
        # ======================================

        if field == "wilaya":

            return sanitize_wilaya(

                text,

                chat_id
            )

        # ======================================
        # 📝 DESCRIPTION
        # ======================================

        if field == "description":

            return sanitize_description(

                text,

                chat_id
            )

        # ======================================
        # 🚫 UNKNOWN FIELD
        # ======================================

        logger.warning(

            "safe_sanitize_unknown_field",

            extra={

                "chat_id": chat_id,

                "field": field
            }
        )

        return None

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
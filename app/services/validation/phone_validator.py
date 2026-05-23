import re

from app.core.logger import (
    logger
)


# ==============================================
# 📞 PHONE NORMALIZER
# ==============================================

def normalize_phone(

    text: str

) -> str:

    # ==========================================
    # 🧹 CLEAN INPUT
    # ==========================================

    text = text.strip()

    text = re.sub(

        r"[\s\-\.\(\)]",

        "",

        text
    )

    # ==========================================
    # 🇩🇿 NORMALIZE ALGERIA PREFIX
    # ==========================================

    if text.startswith("+213"):

        text = "0" + text[4:]

    elif text.startswith("213"):

        text = "0" + text[3:]

    return text

# ==============================================
# 📞 PHONE VALIDATION
# ==============================================

def validate_phone(

    text: str | None,

    chat_id: int | None = None

) -> bool:

    # ==========================================
    # 🚫 NONE INPUT
    # ==========================================

    if text is None:

        logger.warning(

            "phone_none_input",

            extra={
                "chat_id": chat_id
            }
        )

        return False

    # ==========================================
    # 🚫 INVALID TYPE
    # ==========================================

    if not isinstance(text, str):

        logger.warning(

            "phone_invalid_type",

            extra={
                "chat_id": chat_id,
                "input_type": str(type(text))
            }
        )

        return False

    try:

        # ======================================
        # 📞 NORMALIZE PHONE
        # ======================================

        text = normalize_phone(text)

        # ======================================
        # 🇩🇿 ALGERIAN VALIDATION
        # ======================================

        dz_valid = bool(

            re.fullmatch(

                r"0[5-7]\d{8}",

                text
            )
        )

        # ======================================
        # 🌍 INTERNATIONAL VALIDATION
        # ======================================

        international_valid = bool(

            re.fullmatch(

                r"\+?[1-9]\d{7,14}",

                text
            )
        )

        is_valid = dz_valid or international_valid

        # ======================================
        # 🚫 INVALID PHONE
        # ======================================

        if not is_valid:

            logger.warning(

                "phone_invalid_format",

                extra={
                    "chat_id": chat_id,
                    "phone": text
                }
            )

            return False

        # ======================================
        # ✅ SUCCESS
        # ======================================

        logger.info(

            "phone_validation_success",

            extra={
                "chat_id": chat_id,
                "phone": text
            }
        )

        return True

    except Exception as e:

        logger.exception(

            "phone_validation_failed",

            extra={
                "chat_id": chat_id,
                "error": str(e)
            }
        )

        return False
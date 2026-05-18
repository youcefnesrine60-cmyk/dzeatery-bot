import re

from app.helpers.ui_manager import (
    UIManager
)

from app.repositories.state_repo import (
    get_state,
    delete_state
)

from app.repositories.restaurant_repo import (
    save,
    exists
)

from app.core.db import (
    commit,
    rollback
)

from app.core.middleware.rate_limit import (
    rate_limit
)

from app.core.middleware.idempotency import (
    Idempotency
)

from app.core.logger import (
    logger
)


# ==============================================
# 🚫 RATE LIMIT
# ==============================================

@rate_limit(
    limit=2,
    window=15,
    key_prefix="confirm"
)

# ==============================================
# ✅ CONFIRM CALLBACK
# ==============================================

async def confirm_callback(
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    # ==========================================
    # 🛡️ IDEMPOTENCY PROTECTION
    # ==========================================

    allowed = await Idempotency.protect(

        f"confirm:{chat_id}",

        ttl=20
    )

    if not allowed:

        logger.warning(

            "confirm_duplicate_request",

            extra={
                "chat_id": chat_id
            }
        )

        return

    # ==========================================
    # 📦 LOAD STATE
    # ==========================================

    state = get_state(chat_id)

    if not state:

        logger.warning(

            "confirm_state_missing",

            extra={
                "chat_id": chat_id
            }
        )

        return

    # ==========================================
    # ✅ VALIDATION
    # ==========================================

    required = [

        "owner",
        "restaurant",
        "type",
        "phone",
        "wilaya",
        "lat",
        "lng"
    ]

    if not all(k in state for k in required):

        logger.warning(

            "confirm_missing_fields",

            extra={
                "chat_id": chat_id,
                "state": state
            }
        )

        await UIManager.update(

            chat_id,

            message_id,

            "❌ بيانات ناقصة، أعد المحاولة"
        )

        return

    # ==========================================
    # 🚫 DUPLICATE RESTAURANT
    # ==========================================

    if exists(state["restaurant"]):

        logger.info(

            "restaurant_already_exists",

            extra={
                "chat_id": chat_id,
                "restaurant": state["restaurant"]
            }
        )

        await UIManager.update(

            chat_id,

            message_id,

            "❌ هذا المحل مسجل مسبقاً"
        )

        return

    state["chat_id"] = chat_id

    # ==========================================
    # 💾 DATABASE TRANSACTION
    # ==========================================

    try:

        save(state)

        commit()

        logger.info(

            "restaurant_registered",

            extra={
                "chat_id": chat_id,
                "restaurant": state["restaurant"]
            }
        )

    except Exception as e:

        rollback()

        logger.exception(

            "restaurant_registration_failed",

            extra={
                "chat_id": chat_id,
                "restaurant": state.get("restaurant"),
                "error": str(e)
            }
        )

        await UIManager.update(

            chat_id,

            message_id,

            "❌ حدث خطأ أثناء التسجيل، حاول مجددًا."
        )

        return

    # ==========================================
    # 🧹 CLEANUP
    # ==========================================

    try:

        delete_state(chat_id)

    except Exception as e:

        logger.exception(

            "state_cleanup_failed",

            extra={
                "chat_id": chat_id,
                "error": str(e)
            }
        )

    # ==========================================
    # ✅ SUCCESS
    # ==========================================

    await UIManager.update(

        chat_id,

        message_id,

        "🎉 تم تسجيل المحل بنجاح\n\n"
        "📞 سيتم التواصل معكم قريباً بعد مراجعة الطلب."
    )
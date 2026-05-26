from app.services.validation import (
    validate_phone,
    normalize_phone
)

from app.helpers.state_transition import (
    transition_to
)

from app.helpers.ui_manager import (
    UIManager
)

from app.views.ui import (
    back_ui,
    confirm_ui
)

from app.states.owner_states import (
    OwnerStates
)

from app.core.logger import (
    logger
)


# ==============================================
# 📞 PHONE STEP
# ==============================================

async def handle_phone_step(

    *,

    chat_id: int,

    text: str,

    state: dict

) -> None:

    # ==========================================
    # ☎️ NORMALIZE PHONE
    # ==========================================

    normalized_phone = normalize_phone(text)

    # ==========================================
    # 🚫 INVALID PHONE
    # ==========================================

    if not validate_phone(normalized_phone):

        logger.warning(

            "invalid_phone",

            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(

            chat_id = chat_id,

            text = (
                "❌ رقم هاتف غير صحيح.\n\n"
                "📞 مثال صحيح:\n"
                "0551234567"
            ),

            reply_markup = back_ui()
        )

        return

    # ==========================================
    # 💾 SAVE STATE
    # ==========================================

    state["phone"] = normalized_phone

    # ==========================================
    # 🔄 TRANSITION
    # ==========================================

    success = await transition_to(

        chat_id = chat_id,

        state = state,

        next_state = OwnerStates.CONFIRM
    )

    # ==========================================
    # 🚫 TRANSITION FAILED
    # ==========================================

    if not success:

        logger.error(

            "phone_step_transition_failed",

            extra={
                "chat_id": chat_id
            }
        )

        return

    # ==========================================
    # ✅ SUCCESS
    # ==========================================

    logger.info(

        "phone_step_transition_success",

        extra={
            "chat_id": chat_id
        }
    )

    # ==========================================
    # ⚠️ CONFIRM SCREEN
    # ==========================================

    await UIManager.update(

        chat_id = chat_id,

        text = "⚠️ هل تؤكد عملية التسجيل؟",

        reply_markup = confirm_ui()
    )
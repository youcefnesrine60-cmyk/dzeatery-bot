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

    chat_id: int,

    text: str,

    state: dict

) -> None:

    normalized_phone = normalize_phone(text)

    if not validate_phone(normalized_phone):

        logger.warning(

            "invalid_phone",

            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(

            chat_id,

            "❌ رقم هاتف غير صحيح.\n\n"
            "📞 مثال صحيح:\n"
            "0551234567"
        )

        return

    state["phone"] = normalized_phone

    success = await transition_to(

        chat_id,

        state,

        OwnerStates.CONFIRM
    )

    if not success:

        logger.error(

            "phone_step_transition_failed",

            extra={
                "chat_id": chat_id
            }
        )

        return

    logger.info(

        "phone_step_transition_success",

        extra={
            "chat_id": chat_id
        }
    )

    await UIManager.update(

        chat_id,

        "⚠️ هل تؤكد عملية التسجيل؟",

        confirm_ui()
    )
from app.services.validation_service import (
    valid_phone
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

    if not valid_phone(text):

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

    state["phone"] = text

    success = await transition_to(

        chat_id,

        state,

        OwnerStates.CONFIRM
    )

    if not success:
        return

    await UIManager.update(

        chat_id,

        "⚠️ هل تؤكد عملية التسجيل؟",

        confirm_ui()
    )
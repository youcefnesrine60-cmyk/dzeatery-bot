from app.helpers.safe_sanitize import (
    safe_sanitize
)

from app.helpers.state_transition import (
    transition_to
)

from app.helpers.ui_manager import (
    UIManager
)

from app.helpers.message import (
    send_willaya_name
)

from app.states.owner_states import (
    OwnerStates
)

from app.core.logger import (
    logger
)


# ==============================================
# 🏪 RESTAURANT STEP
# ==============================================

async def handle_restaurant_step(

    chat_id: int,

    text: str,

    state: dict

) -> None:

    clean = safe_sanitize(

        chat_id,

        text,

        "restaurant_name"
    )

    if not clean:

        logger.warning(

            "invalid_restaurant_name",

            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(

            chat_id,

            "❌ اسم المحل غير صالح."
        )

        return

    state["restaurant"] = clean

    success = await transition_to(

        chat_id,

        state,

        OwnerStates.WILAYA
    )

    if not success:
        return

    await send_willaya_name(chat_id)
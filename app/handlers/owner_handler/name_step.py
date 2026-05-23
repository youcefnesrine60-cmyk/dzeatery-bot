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
    send_restaurant_name
)

from app.states.owner_states import (
    OwnerStates
)

from app.core.logger import (
    logger
)


# ==============================================
# 👤 OWNER NAME STEP
# ==============================================

async def handle_name_step(

    chat_id: int,

    text: str,

    state: dict

) -> None:

    clean = safe_sanitize(

        chat_id,

        text,

        "owner_name"
    )

    if not clean:

        logger.warning(

            "invalid_owner_name",

            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(

            chat_id,

            "❌ اسم غير صالح."
        )

        return

    state["owner"] = clean

    success = await transition_to(

        chat_id,

        state,

        OwnerStates.RESTAURANT_NAME
    )

    if not success:

        logger.error(

            "transition_failed",

            extra={
                "chat_id": chat_id
            }
        )

        return
    
    logger.info(

        "transition_success",

        extra={
            "chat_id": chat_id
        }
    )

    await send_restaurant_name(chat_id)
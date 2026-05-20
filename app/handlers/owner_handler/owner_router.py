from app.states.owner_states import (
    OwnerStates
)

from app.handlers.owner_handler.name_step import (
    handle_name_step
)

from app.handlers.owner_handler.restaurant_step import (
    handle_restaurant_step
)

from app.handlers.owner_handler.wilaya_step import (
    handle_wilaya_step
)

from app.handlers.owner_handler.phone_step import (
    handle_phone_step
)

from app.core.logger import (
    logger
)

# ==============================================
# 🧠 OWNER STATE ROUTER
# ==============================================

async def handle_owner_state(

    chat_id: int,

    text: str,

    state: dict

) -> None:

    step = state["step"]

    if step == OwnerStates.NAME:

        logger.info(
            "Handling name step for chat_id {chat_id} with text: {text}",
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        await handle_name_step(
            chat_id,
            text,
            state
        )

    elif step == OwnerStates.RESTAURANT_NAME:

        logger.info(
            "Handling restaurant name step for chat_id {chat_id} with text: {text}",
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        await handle_restaurant_step(
            chat_id,
            text,
            state
        )

    elif step == OwnerStates.WILAYA:

        logger.info(
            "Handling wilaya step for chat_id {chat_id} with text: {text}",
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        await handle_wilaya_step(
            chat_id,
            text,
            state
        )

    elif step == OwnerStates.PHONE:

        logger.info(
            "Handling phone step for chat_id {chat_id} with text: {text}",
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        await handle_phone_step(
            chat_id,
            text,
            state
        )
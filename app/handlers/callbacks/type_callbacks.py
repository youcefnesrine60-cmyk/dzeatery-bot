import re

from app.helpers.ui_manager import (
    UIManager
)

from app.repositories.state_repo import (
    get_state,
    set_state
)

from app.states.owner_states import (
    OwnerStates
)

from app.views.texts import (
     PHONE_NUMBRE
)

from app.core.logger import (
    logger
)

from app.views.ui import *

# ==============================================
# 🍽️ TYPE
# ==============================================

async def type_callback(
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    state = get_state(chat_id)

    if not state:

        logger.error(f"State not found for user {chat_id}")
        return

    try:

        state["type"] = callback_data.replace(
            "type_",
            ""
        )

        logger.info(f"User {chat_id} selected type: {state['type']}")

    except Exception as e:

        logger.error(f"Error parsing type for user {chat_id}: {e}")
        return

    try:

        state["history"].append(
            OwnerStates.TYPE
        )

        logger.info(f"User {chat_id} updated history: {state['history']}")

    except Exception as e:
        logger.error(f"Error updating history for user {chat_id}: {e}")
        return

    try:

        state["step"] = OwnerStates.PHONE

        set_state(chat_id, state)
        logger.info(f"User {chat_id} updated step to: {state['step']}")

    except Exception as e:
        logger.error(f"Error updating step for user {chat_id}: {e}")
        return

    logger.info(f"User {chat_id} completed type selection: {state['type']}")
    await UIManager.update(

        chat_id,

        message_id,

        PHONE_NUMBRE,

        back_ui()
    )
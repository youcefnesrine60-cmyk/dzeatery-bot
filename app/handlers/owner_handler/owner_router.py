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

STATE_HANDLERS = {

    OwnerStates.NAME: handle_name_step,

    OwnerStates.RESTAURANT: handle_restaurant_step,

    OwnerStates.WILAYA: handle_wilaya_step,

    OwnerStates.PHONE: handle_phone_step
}

# ==============================================
# 🚀 HANDLE OWNER STATE
# ==============================================

async def handle_owner_state(

    *,

    chat_id: int,

    text: str,

    state: dict

) -> None:

    step = state.get("step")

    handler = STATE_HANDLERS.get(step)

    if not handler:

        logger.warning(

            "unknown_owner_state",

            extra={

                "chat_id": chat_id,

                "step": step
            }
        )

        return

    logger.info(

        "handling_owner_state",

        extra={

            "chat_id": chat_id,
            
            "step": step
        }
    )

    await handler(

        chat_id = chat_id,

        text = text,

        state = state
    )
# ==============================================
# 🧠 OWNER STATE ROUTER
# استقبال حالة المستخدم الحالية 
# وتوجيه الرسالة إلى المعالج المناسب
# ==============================================

from typing import Any, Awaitable, Callable

from app.core.logger import logger

from app.handlers.owner_handler.name_step import handle_name_step
from app.handlers.owner_handler.phone_step import handle_phone_step
from app.handlers.owner_handler.restaurant_step import handle_restaurant_step
from app.handlers.owner_handler.wilaya_step import handle_wilaya_step

from app.states.owner_states import OwnerStates

# ==============================================
# 🧩 TYPES
# ==============================================

StateData = dict[str, Any]

StateHandler = Callable[
    ...,
    Awaitable[None],
]

# ==============================================
# 🧠 OWNER STATE HANDLERS
# ==============================================

STATE_HANDLERS: dict[
    str,
    StateHandler,
] = {
    OwnerStates.NAME: handle_name_step,
    OwnerStates.RESTAURANT: handle_restaurant_step,
    OwnerStates.WILAYA: handle_wilaya_step,
    OwnerStates.PHONE: handle_phone_step,
}

# ==============================================
# 🚀 HANDLE OWNER STATE
# ==============================================

async def handle_owner_state(
    *,
    chat_id: int,
    text: str,
    state: StateData,
    message_id: int,
) -> None:

    # ==========================================
    # 📥 CURRENT STEP
    # ==========================================

    step = state.get(
        "step",
    )

    handler = STATE_HANDLERS.get(
        step,
    )

    # ==========================================
    # 🚫 UNKNOWN STEP
    # ==========================================

    if handler is None:

        logger.warning(
            "unknown_owner_state",
            extra={
                "chat_id": chat_id,
                "step": step,
            },
        )

        return

    # ==========================================
    # 🚀 DISPATCH HANDLER
    # ==========================================

    await handler(
        chat_id=chat_id,
        text=text,
        state=state,
        message_id=message_id,
    )
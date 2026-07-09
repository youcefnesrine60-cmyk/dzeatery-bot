# ==============================================
# 👤 OWNER NAME STEP
# ==============================================

from typing import Any

from app.core.logger import logger

from app.helpers.message import send_restaurant_name
from app.helpers.safe_sanitize import safe_sanitize
from app.helpers.state_transition import transition_to
from app.helpers.ui_manager import UIManager

from app.states.owner_states import OwnerStates

from app.views.ui import back_ui

# ==============================================
# 🧩 TYPES
# ==============================================

StateData = dict[str, Any]

# ==============================================
# 👤 HANDLE OWNER NAME STEP
# ==============================================

async def handle_name_step(
    *,
    chat_id: int,
    text: str,
    state: StateData,
    message_id: int | None = None,
) -> None:

    # ==========================================
    # 🧼 SANITIZE INPUT
    # ==========================================

    clean = safe_sanitize(
        chat_id=chat_id,
        text=text,
        field="owner",
    )

    # ==========================================
    # 🚫 INVALID INPUT
    # ==========================================

    if clean is None:

        logger.warning(
            "invalid_owner",
            extra={
                "chat_id": chat_id,
            },
        )

        await UIManager.update(
            chat_id=chat_id,
            text="❌ الاسم غير صالح.",
            reply_markup=await back_ui(),
        )

        return

    # ==========================================
    # 💾 SAVE STATE
    # ==========================================

    state["owner"] = clean

    # ==========================================
    # 🔄 TRANSITION
    # ==========================================

    if not await transition_to(
        chat_id=chat_id,
        state=state,
        next_state=OwnerStates.RESTAURANT,
    ):
        logger.error(
            "owner_transition_failed",
            extra={
                "chat_id": chat_id,
            },
        )
        return

    # ==========================================
    # 🍽️ REQUEST RESTAURANT NAME
    # ==========================================

    await send_restaurant_name(
        chat_id=chat_id,
        message_id=message_id,
    )
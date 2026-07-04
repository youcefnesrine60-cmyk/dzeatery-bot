# ==============================================
# 🏪 RESTAURANT STEP
# ==============================================

from typing import Any

from app.core.logger import logger

from app.helpers.message import send_wilaya_name
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
# 🏪 HANDLE RESTAURANT STEP
# ==============================================

async def handle_restaurant_step(
    *,
    chat_id: int,
    text: str,
    state: StateData,
) -> None:

    # ==========================================
    # 🧼 SANITIZE INPUT
    # ==========================================

    clean = safe_sanitize(
        chat_id=chat_id,
        text=text,
        field="restaurant",
    )

    # ==========================================
    # 🚫 INVALID INPUT
    # ==========================================

    if clean is None:

        logger.warning(
            "invalid_restaurant",
            extra={
                "chat_id": chat_id,
            },
        )

        await UIManager.update(
            chat_id=chat_id,
            text="❌ اسم المحل غير صالح.",
            reply_markup=await back_ui(),
        )

        return

    # ==========================================
    # 💾 SAVE STATE
    # ==========================================

    state["restaurant"] = clean

    # ==========================================
    # 🔄 TRANSITION
    # ==========================================

    if not await transition_to(
        chat_id=chat_id,
        state=state,
        next_state=OwnerStates.WILAYA,
    ):
        logger.error(
            "restaurant_transition_failed",
            extra={
                "chat_id": chat_id,
            },
        )
        return

    # ==========================================
    # 🗺️ REQUEST WILAYA
    # ==========================================

    await send_wilaya_name(
        chat_id=chat_id,
    )
# ==============================================
# 📍 WILAYA STEP
# ==============================================

from typing import Any

from app.core.logger import logger

from app.helpers.safe_sanitize import safe_sanitize
from app.helpers.state_transition import transition_to
from app.helpers.ui_manager import UIManager

from app.states.owner_states import OwnerStates

from app.views.ui import (
    back_ui,
    location_webapp_ui,
)

# ==============================================
# 🧩 TYPES
# ==============================================

StateData = dict[str, Any]

# ==============================================
# 📍 HANDLE WILAYA STEP
# ==============================================

async def handle_wilaya_step(
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
        field="wilaya",
    )

    # ==========================================
    # 🚫 INVALID INPUT
    # ==========================================

    if clean is None:

        logger.warning(
            "invalid_wilaya",
            extra={
                "chat_id": chat_id,
            },
        )

        await UIManager.update(
            chat_id=chat_id,
            text="❌ الولاية غير صالحة.",
            reply_markup=await back_ui(),
        )

        return

    # ==========================================
    # 💾 SAVE STATE
    # ==========================================

    state["wilaya"] = clean

    # ==========================================
    # 🔄 TRANSITION
    # ==========================================

    if not await transition_to(
        chat_id=chat_id,
        state=state,
        next_state=OwnerStates.LOCATION,
    ):
        logger.error(
            "wilaya_transition_failed",
            extra={
                "chat_id": chat_id,
            },
        )
        return

    # ==========================================
    # 📍 REQUEST LOCATION
    # ==========================================

    await UIManager.update(
        chat_id=chat_id,
        text="📍 اضغط على الزر لتحديد موقع المحل على الخريطة:",
        reply_markup=await location_webapp_ui(),
    )
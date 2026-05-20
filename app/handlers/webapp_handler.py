#====================================
# المسؤول عن:
# استقبال الموقع من Telegram WebApp
#====================================

import json

from app.repositories.state_repo import (
    get_state
)

from app.helpers.ui_manager import (
    UIManager
)

from app.views.ui import (
    types_ui
)

from app.states.owner_states import (
    OwnerStates
)

from app.helpers.state_transition import (
    transition_to
)

from app.core.logger import (
    logger
)

# =====================================================
# 🌍 WEBAPP LOCATION
# =====================================================

async def handle_webapp_data(
    data: dict
) -> None:

    message = data["message"]

    chat_id = message["chat"]["id"]

    state = get_state(chat_id)

    # ==========================================
    # 🚫 NO STATE
    # ==========================================

    if not state:

        logger.warning(

            "webapp_state_missing",

            extra={
                "chat_id": chat_id
            }
        )

        return

    # ==========================================
    # 🚫 INVALID STEP
    # ==========================================

    if state["step"] != OwnerStates.LOCATION:

        logger.warning(

            "invalid_webapp_step",

            extra={
                "chat_id": chat_id,
                "step": state["step"]
            }
        )

        return

    # ==========================================
    # 📍 EXTRACT LOCATION
    # ==========================================

    webapp_data = json.loads(
        message["web_app_data"]["data"]
    )

    state["lat"] = webapp_data["lat"]

    state["lng"] = webapp_data["lng"]

    logger.info(

        "location_saved",

        extra={
            "chat_id": chat_id,
            "lat": state["lat"],
            "lng": state["lng"]
        }
    )

    # ==========================================
    # 🔄 TRANSITION TO TYPE
    # ==========================================

    success = await transition_to(

        chat_id,

        state,

        OwnerStates.TYPE
    )

    if not success:
        return

    # ==========================================
    # 🍽️ SHOW TYPES
    # ==========================================

    await UIManager.update(

        chat_id,

        "📍 تم حفظ موقع المحل بنجاح."
    )

    await UIManager.update(

        chat_id,

        "🍽️ اختر نوع المحل:",

        types_ui()
    )
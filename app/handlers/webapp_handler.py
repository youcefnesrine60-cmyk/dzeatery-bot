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
        
    *,
    data: dict
) -> None:

    message = data["message"]

    chat_id = message["chat"]["id"]

    state = get_state(chat_id = chat_id)

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

        chat_id = chat_id,

        state = state,

        next_state = OwnerStates.TYPE
    )

    if not success:

        logger.error(

            "webapp_transition_failed",

            extra={

                "chat_id": chat_id
            }
        )
        return

    # ==========================================
    # 🍽️ SHOW TYPES
    # ==========================================

    logger.info(

        "webapp_location_saved",

        extra={

            "chat_id": chat_id
        }
    )

    await UIManager.update(

        chat_id = chat_id,

        text = "📍 تم حفظ موقع المحل بنجاح.",

        reply_markup = None
    )

    logger.info(

        "prompting_for_type",

        extra={
            
            "chat_id": chat_id
        }
    )

    await UIManager.update(

        chat_id = chat_id,

        text = "🍽️ اختر نوع المحل:",

        reply_markup = types_ui()
    )
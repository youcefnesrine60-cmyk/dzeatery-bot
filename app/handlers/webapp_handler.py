#====================================
# المسؤول عن:
# استقبال الموقع من Telegram WebApp
#====================================

import json

from app.repositories.state_repo import (
    get_state,
    set_state
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

from app.core.logger import (
    logger
)

# =====================================================
# 🌍 WEBAPP LOCATION 
# =====================================================
async def handle_webapp_data(
        data: dict)-> None:

    message = data["message"]

    chat_id = message["chat"]["id"]

    state = get_state(chat_id)

    if not state:

        logger.warning(

            "Received webapp data for chat_id {chat_id} without existing state.",
            extra={
                "chat_id": chat_id
            }
        )
        return

    if state["step"] != OwnerStates.LOCATION:

        logger.warning(
            "Received webapp data for chat_id {chat_id} but current step is {step}.",
            extra={
                "chat_id": chat_id,
                "step": state["step"]
            }
        )
        return

    webapp_data = json.loads(
        message["web_app_data"]["data"]
    )

    
    state["lat"] = webapp_data["lat"]

    state["lng"] = webapp_data["lng"]

    state["history"].append(OwnerStates.LOCATION)

    state["step"] = OwnerStates.TYPE
    
    set_state(chat_id, state)

    await UIManager.update(
        chat_id,
        "📍 تم حفظ موقع المحل بنجاح."
    )

    await UIManager.update(
        chat_id,
        "🍽️ اختر نوع المحل:",
        types_ui()
    )
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

# =====================================================
# 🌍 WEBAPP LOCATION 
# =====================================================
async def handle_webapp_data(
        data: dict)-> None:

    message = data["message"]

    chat_id = message["chat"]["id"]

    state = get_state(chat_id)

    if not state:
        return

    if state["step"] != OwnerStates.LOCATION:
        return

    webapp_data = json.loads(
        message["web_app_data"]["data"]
    )

    state["lat"] = webapp_data["lat"]

    state["lng"] = webapp_data["lng"]

    state["history"].append("location")

    state["step"] = "type"

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
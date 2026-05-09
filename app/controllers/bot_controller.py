from app.services.telegram_service import send_message
from app.repositories.state_repo import (get_state, set_state)
from app.handlers.message_handle import handle_message
from app.handlers.callback_handler import handle_callback
from app.views.ui import *
from app.logger import logger


# =====================================================
# 🤖 HANDLE UPDATE (MAIN HANDLER)
# =====================================================

def handle_update(data):
    try:
        # =====================================================
        # 📌 CALLBACK QUERY
        # =====================================================
        if "callback_query" in data:
            handle_callback(data)

        # =====================================================
        # 💬 MESSAGES
        # =====================================================

        if "message" in data:
           handle_message(data) 

        # =====================================================
        # 🌍 WEBAPP LOCATION 
        # =====================================================

        if "message" in data and "web_app_data" in data["message"]:

            chat_id = data["message"]["chat"]["id"]

            state = get_state(chat_id)

            if not state or state["step"] != "location":
                    return

            # =*= if state["step"] == "location": =*=
            import json
            webapp_data = json.loads(
                    data["message"]["web_app_data"]["data"]
                )

            state["lat"] = webapp_data["lat"]

            state["lng"] = webapp_data["lng"]

            state["history"].append("location")

            state["step"] = "type"

            set_state(chat_id, state)

            send_message(
                chat_id,
                "📍 تم حفظ موقع المحل بنجاح."
            )

            send_message(
                chat_id,
                "🍽️ اختر نوع المحل:",
                types_ui()
            )

            return
                
    except Exception as e:
        logger.error(f"ERROR: {e}")
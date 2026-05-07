from app.services.telegram_service import *
from app.repositories.state_repo import *
from app.repositories.user_repo import *
from app.repositories.restaurant_repo import *
from app.services.validation_service import valid_phone
from app.services.sanitize_service import sanitize_text
from app.views.ui import *
from app.logger import logger


def go_back(chat_id):
    state = get_state(chat_id)

    if not state or not state.get("history"):
        return None

    prev = state["history"].pop()

    cleanup = {
        "name": ["owner", "restaurant", "wilaya", "lat", "lng", "type", "phone"],
        "restaurant_name": ["restaurant", "wilaya", "lat", "lng", "type", "phone"],
        "wilaya": ["wilaya", "lat", "lng", "type", "phone"],
        "location": ["lat", "lng", "type", "phone"],
        "type": ["type", "phone"],
        "phone": ["phone"],
    }

    for k in cleanup.get(prev, []):
        state.pop(k, None)

    state["step"] = prev
    set_state(chat_id, state)
    return prev

def location_webapp_ui():
    return {
        "inline_keyboard": [
            [{
                "text": "📍 تحديد موقع المحل",
                "web_app": {
                    "url": "https://dzeatery.onrender.com/map"
                }
            }],
            [{"text": "🔙 رجوع", "callback_data": "back_step"}]
        ]
    }

def handle_update(data):
    try:
        # ================= CALLBACK =================
        if "callback_query" in data:
            q = data["callback_query"]
            chat_id = q["message"]["chat"]["id"]
            message_id = q["message"]["message_id"]
            btn = q["data"]

            answer_callback(q["id"])

            # ===== CONSENT =====
            if btn.startswith("consent_"):
                give_consent(chat_id)

                if btn.endswith("owner"):
                    set_state(chat_id, {"step": "name", "history": []})
                    edit_message(chat_id, message_id, "👤 أدخل اسمك الكامل:", back_ui())
                else:
                    edit_message(chat_id, message_id, "🍽️ اختر مطعم:", restaurants_ui())
                return

            # ===== OWNER =====
            if btn == "owner":
                if not has_consent(chat_id):
                    edit_message(chat_id, message_id, consent_text(), consent_ui("owner"))
                    return

                set_state(chat_id, {"step": "name", "history": []})
                edit_message(chat_id, message_id, "👤 أدخل اسمك الكامل:", back_ui())
                return

            # ===== BACK =====
            if btn == "back_main":
                delete_state(chat_id)
                edit_message(chat_id, message_id, "👋 القائمة الرئيسية", main_menu_ui())
                return

            if btn == "back_step":
                prev = go_back(chat_id)

                if not prev:
                    delete_state(chat_id)
                    edit_message(chat_id, message_id, "👋 القائمة الرئيسية", main_menu_ui())
                    return

                if prev == "name":
                    edit_message(chat_id, message_id, "👤 أدخل اسمك الكامل:", back_ui())

                elif prev == "restaurant_name":
                    edit_message(chat_id, message_id, "🏪 أدخل اسم المحل:", back_ui())

                elif prev == "wilaya":
                    edit_message(chat_id, message_id, "📍 أدخل الولاية:", back_ui())

                elif prev == "location":
                    send_message(chat_id,
                        "📍 اضغط على الزر لتحديد موقع المحل على الخريطة:",
                        location_webapp_ui()
                    )

                elif prev == "type":
                    edit_message(chat_id, message_id, "🍽️ اختر النوع:", types_ui())

                elif prev == "phone":
                    edit_message(chat_id, message_id, "📞 أدخل الهاتف:", back_ui())

                return

            # ===== TYPE =====
            if btn.startswith("type_"):
                state = get_state(chat_id)

                state["type"] = btn.replace("type_", "")
                state["history"].append("type")
                state["step"] = "phone"

                set_state(chat_id, state)

                edit_message(chat_id, message_id, "📞 أدخل الهاتف:", back_ui())
                return

            # ===== CONFIRM =====
            if btn == "confirm":
                state = get_state(chat_id)

                if not all(k in state for k in ["owner","restaurant","type","phone","wilaya","lat","lng"]):
                    edit_message(chat_id, message_id, "❌ بيانات ناقصة")
                    return

                if exists(state["restaurant"]):
                    edit_message(chat_id, message_id, "❌ المطعم موجود")
                    return

                state["chat_id"] = chat_id
                save(state)

                delete_state(chat_id)
                edit_message(chat_id, message_id, "🎉 تم التسجيل")
                return

        # ================= MESSAGES =================
        if "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")

            if text == "/start":
                send_message(chat_id, "👋 مرحبا", main_menu_ui())
                return

            state = get_state(chat_id)

            if not state:
                return

            step = state["step"]

            if step == "name":
                state["owner"] = sanitize_text(text)
                state["history"].append("name")
                state["step"] = "restaurant_name"

            elif step == "restaurant_name":
                state["restaurant"] = sanitize_text(text)
                state["history"].append("restaurant_name")
                state["step"] = "wilaya"

            elif step == "wilaya":
                state["wilaya"] = sanitize_text(text)
                state["history"].append("wilaya")
                state["step"] = "location"

                set_state(chat_id, state)

                send_message(chat_id,
                    "📍 اضغط على الزر لتحديد موقع المحل على الخريطة:",
                    location_webapp_ui()
                )
                
                return

            elif step == "phone":
                if not valid_phone(text):
                    send_message(chat_id, "❌ رقم خاطئ")
                    return

                state["phone"] = text
                state["history"].append("phone")
                state["step"] = "confirm"

                send_message(chat_id, "⚠️ تأكيد؟", confirm_ui())
                set_state(chat_id, state)
                return

            set_state(chat_id, state)

        if "web_app_data" in msg:
            data_web = msg["web_app_data"]["data"]

            import json
            coords = json.loads(data_web)

            state = get_state(chat_id)

            if state and state["step"] == "location":
                state["lat"] = coords["lat"]
                state["lng"] = coords["lng"]
                state["history"].append("location")
                state["step"] = "type"

                set_state(chat_id, state)

                send_message(chat_id,
                    "🍽️ اختر النوع:",
                    types_ui()
                )
                return
    
        # ================= LOCATION =================
        if "message" in data and "location" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            state = get_state(chat_id)

            if state and state["step"] == "location":
                loc = data["message"]["location"]

                state["lat"] = loc["latitude"]
                state["lng"] = loc["longitude"]
                state["history"].append("location")
                state["step"] = "type"

                set_state(chat_id, state)

                send_message(chat_id, "🍽️ اختر النوع", types_ui())

    except Exception as e:
        logger.error(f"ERROR: {e}")
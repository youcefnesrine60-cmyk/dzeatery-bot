from services.telegram_service import (
    send_message,
    edit_message,
    answer_callback,
    delete_message
)

from services.validation_service import valid_phone
from services.sanitize_service import sanitize_text

from views.ui import *

from models.restaurant_model import load_restaurants, save_restaurants
from repositories.user_repo import has_consent, give_consent

import logging

user_states = {}

# ================= BACK SYSTEM =================
def go_back(chat_id):
    state = user_states.get(chat_id)

    if not state or not state.get("history"):
        return None

    prev = state["history"].pop()

    cleanup_map = {
        "name": ["owner", "restaurant", "wilaya", "lat", "lng", "type", "phone"],
        "restaurant_name": ["restaurant", "wilaya", "lat", "lng", "type", "phone"],
        "wilaya": ["wilaya", "lat", "lng", "type", "phone"],
        "location": ["lat", "lng", "type", "phone"],
        "type": ["type", "phone"],
        "phone": ["phone"],
    }

    for key in cleanup_map.get(prev, []):
        state.pop(key, None)

    state["step"] = prev
    return prev


# ================= MAIN HANDLER =================
def handle_update(data):
    try:

        # ================= CALLBACK =================
        if "callback_query" in data:
            q = data["callback_query"]

            chat_id = q["message"]["chat"]["id"]
            message_id = q["message"]["message_id"]
            btn = q["data"]

            answer_callback(q["id"])

            # ================= CUSTOMER =================
            if btn == "customer":
                if not has_consent(chat_id):
                    edit_message(chat_id, message_id,
                                 consent_text(),
                                 consent_ui("customer"))
                    return

                restaurants = load_restaurants()

                if not restaurants:
                    edit_message(chat_id, message_id,
                                 "❌ عذراً، قائمة المطاعم غير متوفرة حالياً")
                    return

                edit_message(chat_id, message_id,
                             "🍽️ اختر مطعم:",
                             restaurants_ui())

            # ================= OWNER =================
            elif btn == "owner":
                if not has_consent(chat_id):
                    edit_message(chat_id, message_id,
                                 consent_text(),
                                 consent_ui("owner"))
                    return

                user_states[chat_id] = {"step": "name", "history": []}
                edit_message(chat_id, message_id,
                             "👤 أدخل اسمك الكامل:",
                             back_ui())

            # ================= CONSENT =================
            elif btn.startswith("consent_"):
                give_consent(chat_id)
                role = btn.replace("consent_", "")

                if role == "customer":
                    edit_message(chat_id, message_id,
                                 "🍽️ اختر مطعم:",
                                 restaurants_ui())
                else:
                    user_states[chat_id] = {"step": "name", "history": []}
                    edit_message(chat_id, message_id,
                                 "👤 أدخل اسمك الكامل:",
                                 back_ui())

            # ================= DECLINE =================
            elif btn == "decline":
                edit_message(chat_id, message_id,
                             "❌ لا يمكن استخدام البوت بدون الموافقة على سياسة حماية المعطيات ذات الطابع الشخصي",
                             main_menu_ui())

            # ================= BACK MAIN =================
            elif btn == "back_main":
                edit_message(chat_id, message_id,
                            "👋 القائمة الرئيسية \n\n"
                            "👇 يرجى الضغط على إحدى الخيارين:",
                            main_menu_ui())
                user_states.pop(chat_id, None)

            # ================= BACK STEP =================
            elif btn == "back_step":
                prev = go_back(chat_id)

                if not prev:
                    edit_message(chat_id, message_id,
                                "👋 القائمة الرئيسية \n\n"
                                "👇 يرجى الضغط على إحدى الخيارين:",
                                main_menu_ui())
                    user_states.pop(chat_id, None)
                    return

                steps_ui = {
                    "name": ("👤 أدخل اسمك الكامل:", back_ui()),
                    "restaurant_name": ("🏪 أدخل اسم المحل:", back_ui()),
                    "wilaya": ("📍 أدخل الولاية:", back_ui()),
                    "type": ("🍽️ اختر النوع:", types_ui()),
                    "phone": ("📞 أدخل رقم الهاتف:", back_ui()),
                }

                if prev == "location":
                    send_message(chat_id,
                        "📍 أرسل موقع المحل عبر زر الموقع في تيليغرام",
                        {
                            "keyboard": [
                                [{"text": "📍 إرسال الموقع", "request_location": True}],
                                [{"text": "🔙 رجوع"}]
                            ],
                            "resize_keyboard": True
                        })
                else:
                    text, ui = steps_ui[prev]
                    edit_message(chat_id, message_id, text, ui)

            # ================= TYPE =================
            elif btn.startswith("type_"):
                state = user_states.get(chat_id)
                if not state:
                    return

                state["history"].append("type")
                state["type"] = btn.replace("type_", "")
                state["step"] = "phone"

                edit_message(chat_id, message_id,
                             "📞 أدخل رقم الهاتف:",
                             back_ui())

            # ================= CONFIRM =================
            elif btn == "confirm":
                state = user_states.get(chat_id)
                if not state:
                    return

                required = ["owner", "restaurant", "type", "phone", "wilaya", "lat", "lng"]

                if not all(k in state for k in required):
                    edit_message(chat_id, message_id,
                                 "❌ بيانات ناقصة، أعد التسجيل")
                    return

                restaurants = load_restaurants()
                key = state["restaurant"].lower().strip()

                if key in restaurants:
                    edit_message(chat_id, message_id,
                                 "❌ المطعم مسجل مسبقاً")
                    return

                restaurants[key] = {
                    "owner": state["owner"],
                    "type": state["type"],
                    "phone": state["phone"],
                    "wilaya": state["wilaya"],
                    "location": {"lat": state["lat"], "lng": state["lng"]},
                    "chat_id": chat_id
                }

                save_restaurants(restaurants)

                edit_message(chat_id, message_id,
                             "🎉 تم التسجيل بنجاح!\n📞 سنتواصل معكم للتأكيد")
                user_states.pop(chat_id, None)

        # ================= MESSAGES =================
        if "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "").strip()

            # START
            if text == "/start":
                send_message(chat_id,
                "👋 مرحبا بك في منصة طلب الطعام الذكية 🤖 \n"
            "                  -=- DZ Eatery Bot -=-\n\n"
            "🤖 هذا البوت يساعدك في:\n\n"
            "    1- 🍔  تطلب الأكل بسهولة\n"
            "    2- 🏪  تسجل مطعمك 🎯 وتستقبل الطلبات\n\n"
            "👇 اختر نوعك الآن:",
                main_menu_ui())
                return

            # ================= STATE =================
            if chat_id in user_states:
                state = user_states[chat_id]

                # 🚫 منع الكتابة
                if state["step"] in ["type", "confirm"]:
                    delete_message(chat_id, msg["message_id"])
                    send_message(chat_id, "❌ الرجاء استخدام الأزرار فقط")
                    return

                # NAME
                if state["step"] == "name":
                    clean = sanitize_text(text)
                    if not clean:
                        send_message(chat_id, "❌ اسم غير صالح")
                        return

                    state["owner"] = clean
                    state["history"].append("name")
                    state["step"] = "restaurant_name"

                    send_message(chat_id, "🏪 أدخل اسم المحل:", back_ui())

                # RESTAURANT
                elif state["step"] == "restaurant_name":
                    clean = sanitize_text(text)
                    if not clean:
                        send_message(chat_id, "❌ اسم غير صالح")
                        return

                    state["restaurant"] = clean
                    state["history"].append("restaurant_name")
                    state["step"] = "wilaya"

                    send_message(chat_id, "📍 أدخل الولاية:", back_ui())

                # WILAYA
                elif state["step"] == "wilaya":
                    clean = sanitize_text(text)
                    if not clean:
                        send_message(chat_id, "❌ ولاية غير صالحة")
                        return

                    state["wilaya"] = clean
                    state["history"].append("wilaya")
                    state["step"] = "location"

                    send_message(chat_id,
                                 "📍 أرسل موقع المحل عبر زر الموقع في تيليغرام",
                                 {
                                     "keyboard": [
                                         [{"text": "📍 إرسال الموقع", "request_location": True}],
                                         [{"text": "🔙 رجوع"}]
                                     ],
                                     "resize_keyboard": True
                                 })

                # PHONE
                elif state["step"] == "phone":
                    if not valid_phone(text):
                        send_message(chat_id, "❌ رقم غير صحيح\n\n📞 أدخل رقم هاتف صحيح (مثال: 0551234567)")
                        return

                    state["phone"] = text
                    state["history"].append("phone")
                    state["step"] = "confirm"

                    send_message(chat_id,
                                 "⚠️ هل تؤكد التسجيل؟",
                                 confirm_ui())

        # ================= LOCATION =================
        if "message" in data and "location" in data["message"]:
            chat_id = data["message"]["chat"]["id"]

            if chat_id in user_states:
                state = user_states[chat_id]

                if state["step"] == "location":
                    loc = data["message"]["location"]

                    state["lat"] = loc["latitude"]
                    state["lng"] = loc["longitude"]
                    state["history"].append("location")
                    state["step"] = "type"

                    send_message(chat_id,
                                 "🍽️ اختر النوع:",
                                 {"inline_keyboard": types_ui()["inline_keyboard"]})

                    send_message(chat_id,
                                 "📍 تم استلام الموقع",
                                 {"remove_keyboard": True})

    except Exception as e:
        logging.error(f"ERROR handle_update: {e}")
from app.services.telegram_service import *
from app.repositories.state_repo import *
from app.repositories.user_repo import *
from app.repositories.restaurant_repo import *
from app.services.validation_service import valid_phone
from app.services.sanitize_service import sanitize_text
from app.views.ui import *
from app.logger import logger

# ================= BACK SYSTEM =================
def go_back(chat_id):
    state = get_state(chat_id)

    if not state or not state.get("history"):
        return None

    previous_step = state["history"].pop()

    # تنظيف البيانات حسب المرحلة
    cleanup = {
        "name": ["owner", "restaurant", "wilaya", "lat", "lng", "type", "phone"],
        "restaurant_name": ["restaurant", "wilaya", "lat", "lng", "type", "phone"],
        "wilaya": ["wilaya", "lat", "lng", "type", "phone"],
        "location": ["lat", "lng", "type", "phone"],
        "type": ["type", "phone"],
        "phone": ["phone"],
    }

    for k in cleanup.get(previous_step, []):
        state.pop(k, None)

    state["step"] = previous_step
    set_state(chat_id, state)
    return previous_step

# =====================================================
# 🤖 HANDLE UPDATE (MAIN HANDLER)
# =====================================================

def handle_update(data):
    try:
        # =====================================================
        # 📌 CALLBACK QUERY
        # =====================================================
        if "callback_query" in data:
            query = data["callback_query"]
            chat_id = query["message"]["chat"]["id"]
            message_id = query["message"]["message_id"]

            callback_data = query["data"]

            answer_callback(query["id"])

            # =================================================
            # ✅ CONSENT
            # =================================================
            if callback_data.startswith("consent_"):
                give_consent(chat_id)

                if callback_data.endswith("owner"):
                    set_state(chat_id, {"step": "name", "history": []})
                    edit_message(chat_id, message_id, "👤 أدخل اسمك الكامل:", back_ui())
                else:
                    edit_message(chat_id, message_id, "🍽️ اختر مطعم:", restaurants_ui())

            # =================================================
            # 👤 CUSTOMER
            # =================================================
            elif callback_data == "customer":
                if not has_consent(chat_id):
                    edit_message(chat_id, message_id, consent_text(), consent_ui("customer"))
                    return

                restaurants = get_all_restaurants()

                if not restaurants:
                    edit_message(chat_id, message_id, "❌ عذراً، قائمة المطاعم غير متوفرة حالياً")
                    return

                edit_message(chat_id, message_id, "🍽️ اختر مطعم:", restaurants_ui())

            # =================================================
            # 🏪 OWNER
            # =================================================
            elif callback_data == "owner":
                if not has_consent(chat_id):
                    edit_message(chat_id, message_id, consent_text(), consent_ui("owner"))
                    return

                set_state(chat_id, {"step": "name", "history": []})
                edit_message(chat_id, message_id, "👤 أدخل اسمك الكامل:", back_ui())

            # =================================================
            # ❌ DECLINE
            # =================================================
            elif callback_data == "decline":
                edit_message(chat_id, message_id,
                            "❌ لا يمكن استخدام البوت بدون الموافقة على سياسة حماية المعطيات ذات الطابع الشخصي",
                            main_menu_ui())

            # =================================================
            # 🔙 BACK MAIN
            # =================================================
            elif callback_data == "back_main":
                delete_state(chat_id)
                edit_message(
                    chat_id,
                    message_id,

                    "👋 مرحبا بك في منصة طلب الطعام الذكية\n\n"
                    "👇 يرجى اختيار نوع الحساب:",

                    main_menu_ui()
                )
                delete_state(chat_id)

            # =================================================
            # 🔙 BACK STEP
            # =================================================
            elif callback_data == "back_step":
                previous = go_back(chat_id)

                if not previous:
                    delete_state(chat_id)
                    edit_message(
                    chat_id,
                    message_id,

                        "👋 مرحبا بك في منصة طلب الطعام الذكية\n\n"
                        "👇 يرجى اختيار نوع الحساب:",

                        main_menu_ui()
                    )
                    delete_state(chat_id)
                    return

                steps_ui = {

                    "name": (
                        "👤 أدخل اسمك الكامل:",
                        back_ui()
                    ),

                    "restaurant_name": (
                        "🏪 أدخل اسم المحل:",
                        back_ui()
                    ),

                    "wilaya": (
                        "📍 أدخل الولاية:",
                        back_ui()
                    ),

                    "phone": (
                        "📞 أدخل رقم الهاتف:",
                        back_ui()
                    )
                }

                if previous == "location":

                    send_message(
                        chat_id,

                        "📍 اضغط على الزر لفتح الخريطة واختيار موقع المحل الحقيقي:",

                        location_webapp_ui()
                    )

                elif previous == "type":

                    send_message(
                        chat_id,
                        "🍽️ اختر نوع المحل:",
                        types_ui()
                    )

                else:

                    text, ui = steps_ui[previous]

                    edit_message(
                        chat_id,
                        message_id,
                        text,
                        ui
                    )

            # =================================================
            # 🍽️ TYPE
            # =================================================
            elif callback_data.startswith("type_"):
                state = get_state(chat_id)
                if not state:
                    return

                state["type"] = callback_data.replace("type_", "")
                state["history"].append("type")
                state["step"] = "phone"

                set_state(chat_id, state)

                edit_message(chat_id, message_id, "📞 أدخل الهاتف:", back_ui())

            # =================================================
            # ✅ CONFIRM
            # =================================================
            elif callback_data == "confirm":
                state = get_state(chat_id)
                if not state:
                    return

                required = ["owner", "restaurant", "type", "phone", "wilaya", "lat", "lng"]

                if not all(k in state for k in required):
                    edit_message(chat_id, message_id, "❌ بيانات ناقصة، أعد المحاولة")
                    return

                restaurants = get_all_restaurants()
                key = state["restaurant"].lower().strip()

                if key in restaurants:
                    edit_message(chat_id, message_id, "❌ هذا المحل مسجل مسبقاً")
                    return

                state["chat_id"] = chat_id
                save(state)

                delete_state(chat_id)
                edit_message(
                    chat_id,
                    message_id,

                    "🎉 تم تسجيل المحل بنجاح\n\n"
                    "📞 سيتم التواصل معكم قريباً بعد مراجعة الطلب."
                )

        # =====================================================
        # 💬 MESSAGES
        # =====================================================

        if "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "").strip()

            # =================================================
            # 🚀 START
            # =================================================

            if text == "/start":
                send_message(

                    chat_id,

                    "👋 مرحبا بك في منصة طلب الطعام الذكية 🤖\n\n"

                    "                 -= DZ Eatery Bot =-\n\n"

                    "🤖 هذا البوت يساعدك في:\n\n"

                    "1- 🍔 طلب الطعام بسهولة.\n"
                    "2- 🏪 تسجيل مطعمك واستقبال الطلبات.\n"
                    "3- 📍 إدارة المحل والطلبات.\n"
                    "4- 💳 تطوير نشاطك التجاري رقمياً.\n\n"

                    "👇 اختر نوع الحساب:",

                    main_menu_ui()
                )

                return
            
            # =================================================
            # 🔙 BACK BUTTON
            # =================================================

            if text == "🔙 رجوع":

                previous = go_back(chat_id)

                if not previous:

                    delete_state(chat_id)

                    send_message(

                        chat_id,

                        "👋 مرحبا بك في منصة طلب الطعام الذكية\n\n"
                        "👇 يرجى اختيار نوع الحساب:",

                        main_menu_ui()
                    )

                    return

                return

            # =================================================
            # 🧠 USER STATE FLOW
            # =================================================

            state = get_state(chat_id)

            if not state:
                return

            # =============================================
            # 🚫 PREVENT MANUAL TEXT IN BUTTON STEPS
            # =============================================

            if state["step"] in ["type", "confirm"]:

                delete_message(
                    chat_id,
                    msg["message_id"]
                )

                send_message(
                    chat_id,
                    "❌ الرجاء استعمال الأزرار فقط."
                )

                return

            step = state["step"]

            # =============================================
            # 👤 OWNER NAME
            # ============================================

            if step == "name":
                clean = sanitize_text(text)

                if not clean:

                    send_message(
                        chat_id,
                        "❌ اسم غير صالح."
                    )

                    return

                state["owner"] = clean
                state["history"].append("name")
                state["step"] = "restaurant_name"

                set_state(chat_id, state)

                send_message(
                    chat_id,
                    "🏪 أدخل اسم المحل:",
                    back_ui()
                )

            # =============================================
            # 🏪 RESTAURANT NAME
            # =============================================

            elif step == "restaurant_name":
                clean = sanitize_text(text)

                if not clean:

                    send_message(
                        chat_id,
                        "❌ اسم المحل غير صالح."
                    )

                    return
                
                state["restaurant"] = clean
                state["history"].append("restaurant_name")
                state["step"] = "wilaya"
                set_state(chat_id, state)

                send_message(
                    chat_id,
                    "📍 أدخل الولاية:",
                    back_ui()
                )

            # =============================================
            # 📍 WILAYA
            # =============================================

            elif step == "wilaya":
                clean = sanitize_text(text)

                if not clean:

                    send_message(
                        chat_id,
                        "❌ ولاية غير صالحة."
                    )

                    return
                state["wilaya"] = clean
                state["history"].append("wilaya")
                state["step"] = "location"

                set_state(chat_id, state)

                send_message(chat_id,
                    "📍 اضغط على الزر لتحديد موقع المحل على الخريطة:",
                    location_webapp_ui()
                )
                
            # =============================================
            # 📞 PHONE
            # =============================================
            
            elif step == "phone":
                if not valid_phone(text):
                    send_message(

                        chat_id,

                        "❌ رقم هاتف غير صحيح.\n\n"
                        "📞 مثال صحيح:\n"
                        "0551234567"
                    )
                    return

                state["phone"] = text
                state["history"].append("phone")
                state["step"] = "confirm"

                set_state(chat_id, state)
                send_message(
                    chat_id,
                    "⚠️ هل تؤكد عملية التسجيل؟",
                    confirm_ui()
                )

        # =====================================================
        # 🌍 WEBAPP LOCATION
        # =====================================================

        if "message" in data and "web_app_data" in data["message"]:

            chat_id = data["message"]["chat"]["id"]

            state = get_state(chat_id)

            if not state:
                return

            if state["step"] == "location":

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
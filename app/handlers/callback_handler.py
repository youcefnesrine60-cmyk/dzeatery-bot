from app.services.telegram_service import (
    send_message,
    edit_message,
    answer_callback
)
from app.repositories.state_repo import (
    get_state,
    set_state,
    delete_state
)
from app.repositories.user_repo import (
    has_consent,
    give_consent
)

from app.repositories.restaurant_repo import (
    get_all_restaurants,
    save
)
from app.helpers.message import send_main_menu
from app.controllers.back_system_controller import go_back
from app.views.ui import *

# =====================================================
# 📌 CALLBACK ROUTER
# =====================================================

def handle_callback(data):
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
        edit_message(
            chat_id,
            message_id,
            "❌ لا يمكن استخدام البوت بدون الموافقة على سياسة حماية المعطيات ذات الطابع الشخصي",
            main_menu_ui()
        )

    # =================================================
    # 🔙 BACK MAIN
    # =================================================

    elif callback_data == "back_main":
        delete_state(chat_id)
        edit_message(
            chat_id,
            message_id,
            "👋 مرحبا بك في منصة طلب الطعام الذكية\n\n👇 يرجى اختيار نوع الحساب:",
            main_menu_ui()
        )

    # =================================================
    # 🔙 BACK STEP
    # =================================================

    elif callback_data == "back_step":
        previous = go_back(chat_id)

        if not previous:
            delete_state(chat_id)
            send_main_menu(chat_id)
            return

        steps_ui = {
            "name": ("👤 أدخل اسمك الكامل:", back_ui()),
            "restaurant_name": ("🏪 أدخل اسم المحل:", back_ui()),
            "wilaya": ("📍 أدخل الولاية:", back_ui()),
            "phone": ("📞 أدخل رقم الهاتف:", back_ui())
        }

        if previous == "location":
            send_message(chat_id, "📍 اضغط على الزر لفتح الخريطة واختيار موقع المحل:", location_webapp_ui())

        elif previous == "type":
            send_message(chat_id, "🍽️ اختر نوع المحل:", types_ui())

        else:
            text, ui = steps_ui[previous]
            edit_message(chat_id, message_id, text, ui)

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
            "🎉 تم تسجيل المحل بنجاح\n\n📞 سيتم التواصل معكم قريباً بعد مراجعة الطلب."
        )

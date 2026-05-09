from app.services.telegram_service import (
    send_message,
    delete_message,
)
from app.repositories.state_repo import (
    get_state,
    set_state,
    delete_state
)
from app.services.validation_service import valid_phone
from app.services.sanitize_service import sanitize_text
from app.helpers.message import send_main_menu
from app.controllers.back_system_controller import go_back
from app.views.ui import *

# =====================================================
# 💬 MESSAGE ROUTER
# =====================================================

def handle_message(data):
    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()

    # =================================================
    # 🚀 START
    # =================================================

    if text == "/start":
        send_message(
            chat_id,
            "👋 مرحبا بك في منصة طلب الطعام الذكية 🤖\n\n-= DZ Eatery Bot =-\n\n"
            "🤖 هذا البوت يساعدك في:\n\n"
            "1- 🍔 طلب الطعام بسهولة.\n"
            "2- 🏪 تسجيل مطعمك واستقبال الطلبات.\n"
            "3- 📍 إدارة المحل والطلبات.\n"
            "4- 💳 تطوير نشاطك التجاري رقمياً.\n\n👇 اختر نوع الحساب:",
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
            send_main_menu(chat_id)
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
        delete_message(chat_id, msg["message_id"])
        send_message(chat_id, "❌ الرجاء استعمال الأزرار فقط.")
        return

    step = state["step"]

    # =============================================
    # 👤 OWNER NAME
    # ============================================

    if step == "name":
        clean = sanitize_text(text)
        if not clean:
            send_message(chat_id, "❌ اسم غير صالح.")
            return

        state["owner"] = clean
        state["history"].append("name")
        state["step"] = "restaurant_name"
        set_state(chat_id, state)

        send_message(chat_id, "🏪 أدخل اسم المحل:", back_ui())

    # =============================================
    # 🏪 RESTAURANT NAME
    # =============================================
    
    elif step == "restaurant_name":
        clean = sanitize_text(text)
        if not clean:
            send_message(chat_id, "❌ اسم المحل غير صالح.")
            return

        state["restaurant"] = clean
        state["history"].append("restaurant_name")
        state["step"] = "wilaya"
        set_state(chat_id, state)

        send_message(chat_id, "📍 أدخل الولاية:", back_ui())

    # =============================================
    # 📍 WILAYA
    # =============================================

    elif step == "wilaya":
        clean = sanitize_text(text)
        if not clean:
            send_message(chat_id, "❌ ولاية غير صالحة.")
            return

        state["wilaya"] = clean
        state["history"].append("wilaya")
        state["step"] = "location"
        set_state(chat_id, state)

        send_message(chat_id, "📍 اضغط على الزر لتحديد موقع المحل على الخريطة:", location_webapp_ui())

    # =============================================
    # 📞 PHONE
    # =============================================

    elif step == "phone":
        if not valid_phone(text):
            send_message(chat_id, "❌ رقم هاتف غير صحيح.\n\n📞 مثال صحيح:\n 0551234567")
            return

        state["phone"] = text
        state["history"].append("phone")
        state["step"] = "confirm"
        set_state(chat_id, state)

        send_message(chat_id, "⚠️ هل تؤكد عملية التسجيل؟", confirm_ui())
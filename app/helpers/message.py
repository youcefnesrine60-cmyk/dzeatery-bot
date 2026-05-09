from app.services.telegram_service import (send_message, edit_message)
from app.views.ui import main_menu_ui

# =====================================================
# 🧠 HELPERS
# =====================================================

def send_main_menu(chat_id):
    send_message(
        chat_id,
        "👋 مرحبا بك في منصة طلب الطعام الذكية\n\n👇 يرجى اختيار نوع الحساب:",
        main_menu_ui()
    )

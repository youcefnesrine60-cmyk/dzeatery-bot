from app.views.ui import (
    back_ui
)

from app.views.texts import(
    WELCOME_MSG,
    RESTAU_NAME,
    WILLAYA_NAME
)
from app.views.ui import (
    main_menu_ui
)

from app.helpers.ui_manager import (
    UIManager
)

# =====================================================
# 🧠 HELPERS
# =====================================================

async def send_main_menu(chat_id):
    await UIManager.update(
        chat_id,
        WELCOME_MSG,
        main_menu_ui()
    )

async def send_restau_name(chat_id):
    await UIManager.update(
        chat_id,
        RESTAU_NAME,
        back_ui()
    )

async def send_willaya_name(chat_id):
    await UIManager.update(
        chat_id,
        WILLAYA_NAME,
        back_ui()
    )


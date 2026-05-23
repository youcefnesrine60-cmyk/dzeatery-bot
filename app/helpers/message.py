# =====================================================
# 🧠 UI HELPERS
# =====================================================

from app.core.logger import (
    logger
)

from app.helpers.ui_manager import (
    UIManager
)

from app.views.texts import (
    RESTAU_NAME,
    WELCOME_MSG,
    WILLAYA_NAME
)

from app.views.ui import (
    back_ui,
    main_menu_ui
)

# =====================================================
# 📤 GENERIC SCREEN SENDER
# =====================================================

async def send_screen(

    chat_id: int,

    text: str,

    reply_markup: dict,

    screen_name: str

) -> None:

    logger.info(

        "sending_screen",

        extra={
            "chat_id": chat_id,
            "screen": screen_name
        }
    )

    await UIManager.update(

        chat_id,

        text,

        reply_markup
    )

# =====================================================
# 🏠 MAIN MENU
# =====================================================

async def send_main_menu(

    chat_id: int

) -> None:

    await send_screen(

        chat_id=chat_id,

        text=WELCOME_MSG,

        reply_markup=main_menu_ui(),

        screen_name="main_menu"
    )

# =====================================================
# 🍽️ RESTAURANT NAME
# =====================================================

async def send_restaurant_name(

    chat_id: int

) -> None:

    await send_screen(

        chat_id=chat_id,

        text=RESTAU_NAME,

        reply_markup=back_ui(),

        screen_name="restaurant_name"
    )

# =====================================================
# 🗺️ WILLAYA NAME
# =====================================================

async def send_willaya_name(

    chat_id: int

) -> None:

    await send_screen(

        chat_id=chat_id,

        text=WILLAYA_NAME,

        reply_markup=back_ui(),

        screen_name="willaya_name"
    )
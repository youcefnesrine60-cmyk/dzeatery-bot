# ==============================================
# 🧠 UI HELPERS
# ==============================================

from app.core.logger import logger
from app.helpers.ui_manager import UIManager

from app.views.texts import (
    OWNER_NAME,
    RESTAU_NAME,
    WELCOME_MESSAGE,
    WILAYA_NAME,
)

from app.views.ui import (
    back_ui,
    main_menu_ui,
)

# ==============================================
# 🏷️ TYPES
# ==============================================

ReplyMarkup = dict[str, object]

# ==============================================
# 📤 SEND SCREEN
# ==============================================

async def send_screen(
    *,
    chat_id: int,
    text: str,
    screen_name: str,
    reply_markup: ReplyMarkup | None = None,
    message_id: int | None = None,
) -> None:

    await UIManager.update(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        message_id=message_id,
    )

# ==============================================
# 🏠 MAIN MENU
# ==============================================

async def send_main_menu(
    *,
    chat_id: int,
    message_id: int | None = None,
) -> None:

    logger.info(
        "main_menu_screen",
        extra={
            "chat_id": chat_id,
        },
    )

    await send_screen(
        chat_id=chat_id,
        text=WELCOME_MESSAGE,
        reply_markup=await main_menu_ui(),
        screen_name="main_menu",
        message_id=message_id,
    )

# ==============================================
# 🍽️ RESTAURANT NAME
# ==============================================

async def send_restaurant_name(
    *,
    chat_id: int,
    message_id: int | None = None,
) -> None:

    logger.info(
        "restaurant_name_screen",
        extra={
            "chat_id": chat_id,
        },
    )

    await send_screen(
        chat_id=chat_id,
        text=OWNER_NAME + "\n ✅ تم حفظ الاسم.\nالرجاء متابعة التسجيل.",
        reply_markup=None,
        screen_name="owner name",
        message_id=message_id,
    )

    await send_screen(
        chat_id=chat_id,
        text=RESTAU_NAME +  "\n ✅ message_id : " + str(message_id),
        reply_markup=await back_ui(),
        screen_name="restaurant",
    )
        

# ==============================================
# 🗺️ WILAYA NAME
# ==============================================

async def send_wilaya_name(
    *,
    chat_id: int,
    message_id: int | None = None,
) -> None:

    logger.info(
        "wilaya_screen",
        extra={
            "chat_id": chat_id,
        },
    )

    await send_screen(
        chat_id=chat_id,
        text=WILAYA_NAME,
        reply_markup=await back_ui(),
        screen_name="wilaya",
        message_id=message_id,
    )
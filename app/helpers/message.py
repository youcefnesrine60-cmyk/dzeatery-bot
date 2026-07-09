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
# 📤 SEND SCREEN
# ==============================================

async def send_screen(
    *,
    chat_id: int,
    text: str,
    reply_markup: dict | None = None,
    screen_name: str,
    message_id: int | None = None,
) -> None:

    logger.info(
        "screen_sent",
        extra={
            "chat_id": chat_id,
            "screen": screen_name,
            "message_id": message_id,
        },
    )

    # ✅ تأكد من أن reply_markup هو dict وليس coroutine
    final_reply_markup = None
    if reply_markup is not None:
        # ✅ إذا كان reply_markup هو coroutine، نستخدم await
        if hasattr(reply_markup, "__await__"):
            final_reply_markup = await reply_markup
        else:
            final_reply_markup = reply_markup

    await UIManager.update(
        chat_id=chat_id,
        text=text,
        reply_markup=final_reply_markup,
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
    
    menu_ui = await main_menu_ui()

    await send_screen(
        chat_id=chat_id,
        text=WELCOME_MESSAGE,
        reply_markup=menu_ui,
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
    
    await send_screen(
        chat_id=chat_id,
        text=OWNER_NAME + "\n ✅ تم حفظ الاسم.\nالرجاء متابعة التسجيل.",
        reply_markup=dict(),
        screen_name="owner name",
        message_id=message_id,
    )

    '''await send_screen(
        chat_id=chat_id,
        text=RESTAU_NAME,
        reply_markup=dict(),#await back_ui(),
        screen_name="restaurant",
        message_id=None,
    )'''


# ==============================================
# 🗺️ WILAYA NAME
# ==============================================

async def send_wilaya_name(
    *,
    chat_id: int,
    message_id: int | None = None,
) -> None:

    await send_screen(
        chat_id=chat_id,
        text=WILAYA_NAME,
        reply_markup=await back_ui(),
        screen_name="wilaya",
        message_id=message_id,
    )
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
) -> dict | None:
    """
    إرسال أو تحديث رسالة، وإرجاع الرد من Telegram
    """
    return await UIManager.update(
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
    """
    عرض القائمة الرئيسية
    """
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
) -> int | None:
    """
    إرسال رسالة "أدخل اسم المحل" وإرجاع message_id الخاص بها
    """
    logger.info(
        "restaurant_name_screen",
        extra={
            "chat_id": chat_id,
            "message_id": message_id,
        },
    )

    # 1️⃣ تحديث الرسالة الحالية (إزالة زر الرجوع)
    await send_screen(
        chat_id=chat_id,
        text=OWNER_NAME + "\n ✅ تم حفظ الاسم.",
        reply_markup=None,
        screen_name="owner_name_confirmation",
        message_id=message_id,
    )

    # 2️⃣ إرسال رسالة جديدة (إدخال اسم المحل)
    response = await send_screen(
        chat_id=chat_id,
        text=RESTAU_NAME,
        reply_markup=await back_ui(),
        screen_name="restaurant",
        message_id=None,
    )

    restaurant_message_id = None
    if response and isinstance(response, dict):
        restaurant_message_id = response.get("result", {}).get("message_id")

    if restaurant_message_id:
        logger.info(
            "restaurant_message_sent",
            extra={
                "chat_id": chat_id,
                "restaurant_message_id": restaurant_message_id,
            },
        )

    return restaurant_message_id


# ==============================================
# 🗺️ WILAYA NAME
# ==============================================

async def send_wilaya_name(
    *,
    chat_id: int,
    message_id: int | None = None,
) -> int | None:
    """
    إرسال رسالة "أدخل الولاية" وإرجاع message_id الخاص بها
    """
    logger.info(
        "wilaya_screen",
        extra={
            "chat_id": chat_id,
            "message_id": message_id,
        },
    )

    # 1️⃣ تحديث الرسالة الحالية (إزالة زر الرجوع)
    await send_screen(
        chat_id=chat_id,
        text=RESTAU_NAME + "\n ✅ تم حفظ اسم المحل.",
        reply_markup=None,
        screen_name="restaurant_name_confirmation",
        message_id=message_id,
    )

    # 2️⃣ إرسال رسالة جديدة (إدخال الولاية)
    response = await send_screen(
        chat_id=chat_id,
        text=WILAYA_NAME,
        reply_markup=await back_ui(),
        screen_name="wilaya",
        message_id=None,
    )

    wilaya_message_id = None
    if response and isinstance(response, dict):
        wilaya_message_id = response.get("result", {}).get("message_id")

    if wilaya_message_id:
        logger.info(
            "wilaya_message_sent",
            extra={
                "chat_id": chat_id,
                "wilaya_message_id": wilaya_message_id,
            },
        )

    return wilaya_message_id
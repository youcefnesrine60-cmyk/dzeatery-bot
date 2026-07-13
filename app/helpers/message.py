# ==============================================
# 🧠 UI HELPERS - VERSION PRO
# ==============================================

from typing import Any

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

ReplyMarkup = dict[str, object] | None


# ==============================================
# 📤 SEND SCREEN
# ==============================================

async def send_screen(
    *,
    chat_id: int,
    text: str,
    screen_name: str,
    reply_markup: ReplyMarkup = None,
    message_id: int | None = None,
    store_message_id: bool = True,
) -> dict | None:
    """
    إرسال أو تحديث رسالة مع دعم كامل للإمكانيات الجديدة

    Args:
        chat_id: معرف المستخدم
        text: نص الرسالة
        screen_name: اسم الشاشة للتسجيل
        reply_markup: أزرار تفاعلية
        message_id: معرف الرسالة للتعديل (اختياري)
        store_message_id: تخزين message_id في الحالة (افتراضي True)

    Returns:
        dict | None: رد من Telegram
    """
    return await UIManager.update(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
        message_id=message_id,
        store_message_id=store_message_id,
    )


# ==============================================
# 🏠 MAIN MENU
# ==============================================

async def send_main_menu(
    *,
    chat_id: int,
    message_id: int | None = None,
    cleanup: bool = True,
) -> None:
    """
    عرض القائمة الرئيسية مع تنظيف اختياري

    Args:
        chat_id: معرف المستخدم
        message_id: معرف الرسالة للتعديل (اختياري)
        cleanup: تنظيف الرسائل السابقة (افتراضي True)
    """
    logger.info(
        "main_menu_screen",
        extra={
            "chat_id": chat_id,
            "message_id": message_id,
        },
    )

    # تنظيف الرسائل السابقة
    if cleanup and message_id is None:
        await UIManager.cleanup_messages(chat_id=chat_id)

    await send_screen(
        chat_id=chat_id,
        text=WELCOME_MESSAGE,
        reply_markup=await main_menu_ui(),
        screen_name="main_menu",
        message_id=message_id,
        store_message_id=True,
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
    إرسال رسالة "أدخل اسم المحل" بطريقة محسنة

    Args:
        chat_id: معرف المستخدم
        message_id: معرف الرسالة السابقة للتعديل

    Returns:
        int | None: معرف الرسالة الجديدة
    """
    logger.info(
        "restaurant_name_screen",
        extra={
            "chat_id": chat_id,
            "previous_message_id": message_id,
        },
    )

    # 1️⃣ تعديل الرسالة السابقة للتأكيد
    if message_id:
        await UIManager.edit(
            chat_id=chat_id,
            message_id=message_id,
            text=OWNER_NAME + "\n ✅ تم حفظ الاسم.",
            reply_markup=None,
        )

    # 2️⃣ إرسال رسالة جديدة لإدخال اسم المحل
    response = await UIManager.send_new_message(
        chat_id=chat_id,
        text=RESTAU_NAME,
        reply_markup=await back_ui(),
        store_message_id=True,
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
    إرسال رسالة "أدخل الولاية" بطريقة محسنة

    Args:
        chat_id: معرف المستخدم
        message_id: معرف الرسالة السابقة للتعديل

    Returns:
        int | None: معرف الرسالة الجديدة
    """
    logger.info(
        "wilaya_screen",
        extra={
            "chat_id": chat_id,
            "previous_message_id": message_id,
        },
    )

    # 1️⃣ تعديل الرسالة السابقة للتأكيد
    if message_id:
        await UIManager.edit(
            chat_id=chat_id,
            message_id=message_id,
            text=RESTAU_NAME + "\n ✅ تم حفظ اسم المحل.",
            reply_markup=None,
        )

    # 2️⃣ إرسال رسالة جديدة لإدخال الولاية
    response = await UIManager.send_new_message(
        chat_id=chat_id,
        text=WILAYA_NAME,
        reply_markup=await back_ui(),
        store_message_id=True,
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


# ==============================================
# 🧹 CLEANUP USER SCREENS
# ==============================================

async def cleanup_user_screens(
    *,
    chat_id: int,
    preserve_message_id: int | None = None,
) -> bool:
    """
    تنظيف جميع رسائل المستخدم

    Args:
        chat_id: معرف المستخدم
        preserve_message_id: معرف الرسالة التي لا تريد حذفها

    Returns:
        bool: True إذا تم التنظيف بنجاح
    """
    return await UIManager.cleanup_messages(
        chat_id=chat_id,
        preserve_message_id=preserve_message_id,
    )
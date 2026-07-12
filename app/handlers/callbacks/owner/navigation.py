# ==============================================
# 🔙 NAVIGATION
# ==============================================

import re

from app.core.logger import logger

from app.helpers.navigation import go_back
from app.helpers.state_helper import get_user_state, update_state_field
from app.helpers.ui_manager import UIManager

from app.repositories.state_repo import delete_state

from app.services.telegram import delete_message

from app.states.owner_states import OwnerStates

from app.views.texts import (
    OWNER_NAME,
    PHONE_NUMBER,
    RESTAU_NAME,
    WELCOME_MESSAGE,
    WILAYA_NAME,
)

from app.views.ui import (
    back_ui,
    location_webapp_ui,
    main_menu_ui,
    types_ui,
)

# ==============================================
# 🧹 CLEANUP USER MESSAGES
# ==============================================

async def _cleanup_messages(
    *,
    chat_id: int,
) -> None:
    """
    حذف جميع الرسائل المخزنة للمستخدم
    """
    state = await get_user_state(chat_id=chat_id)

    if not state:
        return

    message_ids = state.get("message_ids")

    if not isinstance(message_ids, list):
        return

    for msg_id in message_ids:
        try:
            await delete_message(
                chat_id=chat_id,
                message_id=msg_id,
            )
        except Exception as e:
            logger.warning(
                "delete_message_failed",
                extra={
                    "chat_id": chat_id,
                    "message_id": msg_id,
                    "error": str(e),
                },
            )

    # مسح القائمة بعد الحذف
    await update_state_field(
        chat_id=chat_id,
        key="message_ids",
        value=[],
    )


# ==============================================
# 🔙 BACK MAIN
# ==============================================

async def back_main_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match,
) -> None:
    """
    العودة إلى القائمة الرئيسية مع حذف جميع الرسائل السابقة
    """
    try:
        # 🧹 حذف جميع الرسائل المخزنة
        await _cleanup_messages(chat_id=chat_id)

        # 🗑️ حذف الحالة بالكامل
        await delete_state(chat_id=chat_id)

        logger.info(
            "back_to_main_menu",
            extra={
                "chat_id": chat_id,
            },
        )

        # ✅ إرسال رسالة جديدة للقائمة الرئيسية (بدون message_id)
        await UIManager.update(
            chat_id=chat_id,
            text=WELCOME_MESSAGE,
            reply_markup=await main_menu_ui(),
            # ❌ لا نمرر message_id لنرسل رسالة جديدة
        )

    except Exception as e:
        logger.exception(
            "back_to_main_menu_failed",
            extra={
                "chat_id": chat_id,
                "error": str(e),
            },
        )


# ==============================================
# ❌ DECLINE
# ==============================================

async def decline_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match,
) -> None:
    """
    رفض الموافقة على الشروط
    """
    logger.info(
        "owner_declined_consent",
        extra={
            "chat_id": chat_id,
        },
    )

    await UIManager.update(
        chat_id=chat_id,
        text="❌ نعتذر! لا يمكن استخدام البوت بدون الموافقة على سياسة حماية المعطيات ذات الطابع الشخصي",
        reply_markup=await main_menu_ui(),
        message_id=message_id,
    )


# ==============================================
# 🔙 BACK STEP
# ==============================================

async def back_step_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match,
) -> None:
    """
    العودة إلى الخطوة السابقة مع حذف جميع الرسائل السابقة
    """
    # 🧹 حذف جميع الرسائل المخزنة
    await _cleanup_messages(chat_id=chat_id)

    # 🔙 العودة إلى الخطوة السابقة
    previous = await go_back(chat_id=chat_id)

    # ==========================================
    # 🏠 NO PREVIOUS STEP → MAIN MENU
    # ==========================================

    # ✅ حذف الحالة
    await delete_state(chat_id=chat_id)

    logger.info(
        "back_button_pressed_no_previous",
        extra={
            "chat_id": chat_id,
        },
    )

    # ✅ إرسال القائمة الرئيسية
    await UIManager.update(
        chat_id=chat_id,
        text=WELCOME_MESSAGE,
        reply_markup=await main_menu_ui(),
    )
    
    # ==========================================
    # 📝 TEXT STEPS
    # ==========================================

    steps_text = {
        OwnerStates.NAME: OWNER_NAME,
        OwnerStates.RESTAURANT: RESTAU_NAME,
        OwnerStates.WILAYA: WILAYA_NAME,
        OwnerStates.PHONE: PHONE_NUMBER,
    }

    # ==========================================
    # 📍 LOCATION STEP
    # ==========================================

    if previous == OwnerStates.LOCATION:
        logger.info(
            "went_back_to_location_step",
            extra={
                "chat_id": chat_id,
            },
        )

        # ✅ إرسال رسالة جديدة لخطوة الموقع
        await UIManager.update(
            chat_id=chat_id,
            text="📍 اضغط على الزر لفتح الخريطة واختيار موقع المحل الحقيقي:",
            reply_markup=await location_webapp_ui(),
            # ❌ لا نمرر message_id لنرسل رسالة جديدة
        )

    # ==========================================
    # 🍽️ TYPE STEP
    # ==========================================

    elif previous == OwnerStates.TYPE:
        logger.info(
            "went_back_to_type_step",
            extra={
                "chat_id": chat_id,
            },
        )

        # ✅ إرسال رسالة جديدة لخطوة النوع
        await UIManager.update(
            chat_id=chat_id,
            text="🍽️ اختر نوع المحل:",
            reply_markup=await types_ui(),
            # ❌ لا نمرر message_id لنرسل رسالة جديدة
        )

    # ==========================================
    # 📝 TEXT INPUT STEP
    # ==========================================

    elif previous in steps_text:
        logger.info(
            "went_back_to_previous_step",
            extra={
                "chat_id": chat_id,
                "step": previous,
            },
        )

        # ✅ إرسال رسالة جديدة للخطوة السابقة
        await UIManager.update(
            chat_id=chat_id,
            text=steps_text[previous],
            reply_markup=await back_ui(),
            # ❌ لا نمرر message_id لنرسل رسالة جديدة
        )

    # ==========================================
    # 🚫 UNKNOWN STEP
    # ==========================================

    else:
        logger.warning(
            "unknown_step_on_back",
            extra={
                "chat_id": chat_id,
                "step": previous,
            },
        )

        # ✅ إرسال رسالة جديدة للقائمة الرئيسية
        await UIManager.update(
            chat_id=chat_id,
            text=WELCOME_MESSAGE,
            reply_markup=await main_menu_ui(),
            # ❌ لا نمرر message_id لنرسل رسالة جديدة
        )
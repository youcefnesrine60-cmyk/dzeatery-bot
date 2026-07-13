# ==============================================
# 🔙 NAVIGATION - VERSION PRO
# ==============================================

import re

from app.core.logger import logger

from app.helpers.navigation import go_back
from app.helpers.state_helper import clear_user_state
from app.helpers.ui_manager import UIManager

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
# 🧩 TYPES
# ==============================================

ReplyMarkup = dict[str, object] | None


# ==============================================
# 🔙 BACK TO MAIN MENU
# ==============================================

async def back_to_main_menu(
    *,
    chat_id: int,
    current_message_id: int | None = None,
    show_welcome: bool = True,
) -> bool:
    """
    العودة إلى القائمة الرئيسية مع تنظيف شامل

    Args:
        chat_id: معرف المحادثة
        current_message_id: معرف الرسالة الحالية (سيتم حذفها)
        show_welcome: عرض رسالة الترحيب أو لا

    Returns:
        bool: True إذا تمت العملية بنجاح
    """
    try:
        # 🧹 تنظيف جميع الرسائل
        await UIManager.cleanup_messages(
            chat_id=chat_id,
            preserve_message_id=None,
        )

        # 🗑️ حذف الحالة بالكامل
        await clear_user_state(chat_id=chat_id)

        logger.info(
            "back_to_main_menu",
            extra={
                "chat_id": chat_id,
            },
        )

        # ✅ إرسال القائمة الرئيسية
        text = WELCOME_MESSAGE if show_welcome else "🏠 القائمة الرئيسية"

        await UIManager.send_new_message(
            chat_id=chat_id,
            text=text,
            reply_markup=await main_menu_ui(),
        )

        return True

    except Exception as e:
        logger.exception(
            "back_to_main_menu_failed",
            extra={
                "chat_id": chat_id,
                "error": str(e),
            },
        )
        return False


# ==============================================
# 🔙 BACK STEP CALLBACK
# ==============================================

async def back_step_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match,
) -> None:
    """
    العودة إلى الخطوة السابقة مع إدارة ذكية للرسائل
    """
    try:
        # 🧹 حذف الرسائل السابقة مع الاحتفاظ بالرسالة الحالية
        await UIManager.cleanup_messages(
            chat_id=chat_id,
            preserve_message_id=message_id,
        )

        # 🔙 العودة إلى الخطوة السابقة
        previous_step = await go_back(chat_id=chat_id)

        # ==========================================
        # 🏠 NO PREVIOUS STEP → MAIN MENU
        # ==========================================

        if not previous_step:
            logger.info(
                "back_button_no_previous_step",
                extra={
                    "chat_id": chat_id,
                    "step": previous_step,
                },
            )

            # حذف الرسالة الحالية
            await UIManager.delete(
                chat_id=chat_id,
                message_id=message_id,
            )

            # العودة إلى القائمة الرئيسية
            await back_to_main_menu(
                chat_id=chat_id,
                current_message_id=None,
                show_welcome=True,
            )
            return

        # ==========================================
        # 📝 TEXT STEPS MAPPING
        # ==========================================

        STEPS_TEXT = {
            OwnerStates.NAME: OWNER_NAME,
            OwnerStates.RESTAURANT: RESTAU_NAME,
            OwnerStates.WILAYA: WILAYA_NAME,
            OwnerStates.PHONE: PHONE_NUMBER,
        }

        # ==========================================
        # 📍 LOCATION STEP
        # ==========================================

        if previous_step == OwnerStates.LOCATION:
            logger.info(
                "back_to_location_step",
                extra={
                    "chat_id": chat_id,
                    "step": previous_step,
                },
            )

            # تحديث الرسالة الحالية
            await UIManager.edit(
                chat_id=chat_id,
                message_id=message_id,
                text="📍 اضغط على الزر لفتح الخريطة واختيار موقع المحل:",
                reply_markup=await location_webapp_ui(),
            )

        # ==========================================
        # 🍽️ TYPE STEP
        # ==========================================

        elif previous_step == OwnerStates.TYPE:
            logger.info(
                "back_to_type_step",
                extra={
                    "chat_id": chat_id,
                    "step": previous_step,
                },
            )

            await UIManager.edit(
                chat_id=chat_id,
                message_id=message_id,
                text="🍽️ اختر نوع المحل:",
                reply_markup=await types_ui(),
            )

        # ==========================================
        # 📝 TEXT INPUT STEP
        # ==========================================

        elif previous_step in STEPS_TEXT:
            logger.info(
                "back_to_text_step",
                extra={
                    "chat_id": chat_id,
                    "step": previous_step,
                },
            )

            await UIManager.edit(
                chat_id=chat_id,
                message_id=message_id,
                text=STEPS_TEXT[previous_step],
                reply_markup=await back_ui(),
            )

        # ==========================================
        # 🚫 UNKNOWN STEP
        # ==========================================

        else:
            logger.warning(
                "unknown_step_on_back",
                extra={
                    "chat_id": chat_id,
                    "step": previous_step,
                },
            )

            # حذف الرسالة الحالية والعودة للقائمة
            await UIManager.delete(
                chat_id=chat_id,
                message_id=message_id,
            )

            await back_to_main_menu(
                chat_id=chat_id,
                current_message_id=None,
                show_welcome=True,
            )

    except Exception as e:
        logger.exception(
            "back_step_callback_failed",
            extra={
                "chat_id": chat_id,
                "message_id": message_id,
                "error": str(e),
            },
        )

        # في حالة الخطأ، نحاول العودة للقائمة الرئيسية
        try:
            await back_to_main_menu(
                chat_id=chat_id,
                current_message_id=message_id,
                show_welcome=True,
            )
        except Exception as fallback_error:
            logger.error(
                "back_step_fallback_failed",
                extra={
                    "chat_id": chat_id,
                    "error": str(fallback_error),
                },
            )


# ==============================================
# 🔙 BACK MAIN CALLBACK
# ==============================================

async def back_main_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match,
) -> None:
    """
    نقطة الدخول للعودة إلى القائمة الرئيسية
    """
    await back_to_main_menu(
        chat_id=chat_id,
        current_message_id=message_id,
        show_welcome=True,
    )


# ==============================================
# ❌ DECLINE CALLBACK
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
    try:
        logger.info(
            "owner_declined_consent",
            extra={
                "chat_id": chat_id,
            },
        )

        # تنظيف الرسائل
        await UIManager.cleanup_messages(
            chat_id=chat_id,
            preserve_message_id=message_id,
        )

        # تحديث الرسالة الحالية
        await UIManager.edit(
            chat_id=chat_id,
            message_id=message_id,
            text="❌ نعتذر! لا يمكن استخدام البوت بدون الموافقة على سياسة حماية المعطيات",
            reply_markup=await main_menu_ui(),
        )

        # حذف الحالة
        await clear_user_state(chat_id=chat_id)

    except Exception as e:
        logger.exception(
            "decline_callback_failed",
            extra={
                "chat_id": chat_id,
                "error": str(e),
            },
        )
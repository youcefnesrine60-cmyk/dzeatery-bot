# ==============================================
# 🏪 OWNER CALLBACKS - VERSION PRO
# Owner Registration & Consent Flow
# ==============================================

import re

from app.core.logger import logger
from app.helpers.state_helper import clear_user_state
from app.helpers.ui_manager import UIManager
from app.repositories.state_repo import set_state
from app.repositories.user_repo import give_consent, has_consent
from app.states.owner_states import OwnerStates
from app.handlers.callbacks.customer.restaurant_list import show_restaurants
from app.views.texts import OWNER_NAME
from app.views.ui import back_ui, consent_text, consent_ui


# ==============================================
# 👤 OWNER CALLBACK
# ==============================================

async def owner_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match[str],
) -> None:
    """
    معالجة اختيار "صاحب محل" من القائمة الرئيسية

    Args:
        chat_id: معرف المستخدم
        message_id: معرف الرسالة
        callback_data: بيانات الكولباك
        match: تطابق النمط
    """
    logger.info(
        "owner_callback_triggered",
        extra={
            "chat_id": chat_id,
            "message_id": message_id,
        },
    )

    # ==========================================
    # 🚫 CONSENT REQUIRED
    # ==========================================

    if not await has_consent(chat_id=chat_id):
        logger.info(
            "owner_consent_required",
            extra={
                "chat_id": chat_id,
            },
        )

        # تنظيف الرسائل السابقة
        await UIManager.cleanup_messages(chat_id=chat_id)

        # إرسال رسالة الموافقة
        await UIManager.send_new_message(
            chat_id=chat_id,
            text=await consent_text(),
            reply_markup=await consent_ui(role="owner"),
            store_message_id=True,
        )
        return

    # ==========================================
    # 🧹 CLEANUP PREVIOUS STATE
    # ==========================================

    await clear_user_state(chat_id=chat_id)
    await UIManager.cleanup_messages(chat_id=chat_id)

    # ==========================================
    # 🚀 START OWNER FLOW
    # ==========================================

    await set_state(
        chat_id=chat_id,
        state={
            "flow": "owner",
            "step": OwnerStates.NAME,
            "history": [],
            "bot_message_id": message_id,
        },
    )

    logger.info(
        "owner_flow_started",
        extra={
            "chat_id": chat_id,
        },
    )

    # إرسال رسالة جديدة لإدخال الاسم
    await UIManager.send_new_message(
        chat_id=chat_id,
        text=OWNER_NAME,
        reply_markup=await back_ui(),
        store_message_id=True,
    )


# ==============================================
# ✅ CONSENT CALLBACK
# ==============================================

async def consent_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match[str],
) -> None:
    """
    معالجة الموافقة على الشروط بطريقة محسنة

    Args:
        chat_id: معرف المستخدم
        message_id: معرف الرسالة
        callback_data: بيانات الكولباك
        match: تطابق النمط
    """
    # تسجيل الموافقة
    await give_consent(chat_id=chat_id)

    # تنظيف الرسائل السابقة (باستثناء الرسالة الحالية)
    await UIManager.cleanup_messages(
        chat_id=chat_id,
        preserve_message_id=message_id,
    )

    if callback_data.endswith("owner"):
        logger.info(
            "owner_consent_accepted",
            extra={
                "chat_id": chat_id,
            },
        )

        # تنظيف الحالة السابقة
        await clear_user_state(chat_id=chat_id)

        # إنشاء حالة جديدة
        await set_state(
            chat_id=chat_id,
            state={
                "flow": "owner",
                "step": OwnerStates.NAME,
                "history": [],
                "bot_message_id": message_id,
            },
        )

        # تعديل الرسالة الحالية
        await UIManager.edit(
            chat_id=chat_id,
            message_id=message_id,
            text=OWNER_NAME,
            reply_markup=await back_ui(),
        )
        return

    # ==========================================
    # 👤 CUSTOMER CONSENT
    # ==========================================

    logger.info(
        "customer_consent_accepted",
        extra={
            "chat_id": chat_id,
        },
    )

    # تعديل الرسالة الحالية لعرض قائمة المطاعم
    await show_restaurants(
        chat_id=chat_id,
        message_id=message_id,
    )
# ==============================================
# 🔙 NAVIGATION
# ==============================================

import re

from app.helpers.ui_manager import UIManager
from app.repositories.state_repo import delete_state
from app.helpers.navigation import go_back

from app.views.texts import (
    WELCOME_MSG,
    OWNER_NAME,
    RESTAU_NAME,
    WILAYA_NAME,
    PHONE_NUMBER
)
from app.views.ui import *
from app.core.logger import logger

# ==============================================
# 🔙 BACK MAIN
# ==============================================

async def back_main_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    try:

        await delete_state(
            chat_id = chat_id
        )

        logger.info(
            " go_back_to_main_menu",
            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(
            chat_id = chat_id,
            text = WELCOME_MSG,
            reply_markup = await main_menu_ui(),
            message_id = message_id
        )
    except Exception as e:

        logger.exception(
            "back_to_main_menu_failed",
            extra={
                "chat_id": chat_id,
                "error": str(e)
            }
        )

# ==============================================
# ❌ DECLINE
# ==============================================

async def decline_callback(        
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match

) -> None:
    
    logger.info(
        "owner_declined_consent",
        extra={
            "chat_id": chat_id
        }
    )

    await UIManager.update(
        chat_id = chat_id,
        text = "❌ نعتذر! لا يمكن استخدام البوت بدون الموافقة على سياسة حماية المعطيات ذات الطابع الشخصي",
        reply_markup = await main_menu_ui(),
        message_id = message_id
    )

# ==============================================
# 🔙 BACK STEP
# ==============================================

async def back_step_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    previous = await go_back(
        chat_id = chat_id
    )

    if not previous:

        try:

            await delete_state(
                chat_id = chat_id
            )

            logger.info(
                "back_button_pressed_no_previous",
                extra={
                    "chat_id": chat_id
                }
            )

            await UIManager.update(
                chat_id = chat_id,
                text = WELCOME_MSG,
                reply_markup = await main_menu_ui(),
                message_id = message_id
            )

            return
        
        except Exception as e:

            logger.exception(
                "back_button_pressed_cleanup_failed",
                extra={
                    "chat_id": chat_id,
                    "error": str(e)
                }
            )
            return

    try:
        
        steps_ui = {

            "name": (
                OWNER_NAME,
                await back_ui()
            ),

            "restaurant": (
                RESTAU_NAME,
                await back_ui()
            ),

            "wilaya": (
                WILAYA_NAME,
                await back_ui()
            ),

            "phone": (
                PHONE_NUMBER,
                await back_ui()
            )
        }

    except Exception as e:

        logger.exception(
            "error_loading_steps_ui",
            extra={
                "chat_id": chat_id,
                "error": str(e)
            }
        )

    if previous == "location":

        logger.info(
            "went_back_to_location_step",
            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(
            chat_id = chat_id,
            text = "📍 اضغط على الزر لفتح الخريطة واختيار موقع المحل الحقيقي:",
            reply_markup = await location_webapp_ui()
        )

    elif previous == "type":

        logger.info(
            "went_back_to_type_step",
            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(
            chat_id = chat_id,
            text = "🍽️ اختر نوع المحل:",
            reply_markup = await types_ui()
        )

    else:
        text, ui = steps_ui[previous]

        logger.info(
            "went_back_to_previous_step",
            extra={
                "chat_id": chat_id,
                "step": previous
            }
        )

        await UIManager.update(
            chat_id = chat_id,
            text = text,
            reply_markup = ui,
            message_id = message_id
        )
# ==============================================
# 🔙 NAVIGATION
# ==============================================

import re

from app.helpers.ui_manager import (
    UIManager
)

from app.repositories.state_repo import (
    delete_state
)

from app.helpers.navigation import (
    go_back
)

from app.views.texts import (
    WELCOME_MSG,
    OWNER_NAME,
    RESTAU_NAME,
    WILLAYA_NAME,
    PHONE_NUMBRE
)

from app.views.ui import *

from app.core.logger import (
    logger
)

# ==============================================
# 🔙 BACK MAIN
# ==============================================

async def back_main_callback(
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    try:

        delete_state(chat_id)

        logger.info(
            "User {chat_id} went back to main menu",
            extra={"chat_id": chat_id}
        )

        await UIManager.update(

            chat_id,

            message_id,

            WELCOME_MSG,

            main_menu_ui()
        )
    except Exception as e:

        logger.error(
            "Error in back_main_callback: {error}",
            extra={"chat_id": chat_id, "error": str(e)}
        )


# ==============================================
# ❌ DECLINE
# ==============================================

async def decline_callback(
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    await UIManager.update(

        chat_id,

        message_id,

        "❌ لا يمكن استخدام البوت بدون الموافقة على سياسة حماية المعطيات ذات الطابع الشخصي",

        main_menu_ui()
    )


# ==============================================
# 🔙 BACK STEP
# ==============================================

async def back_step_callback(
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    previous = go_back(chat_id)

    if not previous:

        try:

            delete_state(chat_id)

            logger.info(
                "User {chat_id} went back to main menu from an unknown state",
                extra={"chat_id": chat_id}
            )

            await UIManager.update(

                chat_id,

                message_id,

                WELCOME_MSG,

                main_menu_ui()
            )

            return
        except Exception as e:

            logger.error(
                "Error in back_step_callback: {error}",
                extra={"chat_id": chat_id, "error": str(e)}
            )

            return

    steps_ui = {

        "name": (
            OWNER_NAME,
            back_ui()
        ),

        "restaurant_name": (
            RESTAU_NAME,
            back_ui()
        ),

        "wilaya": (
            WILLAYA_NAME,
            back_ui()
        ),

        "phone": (
            PHONE_NUMBRE,
            back_ui()
        )
    }

    if previous == "location":

        logger.info(
            "User {chat_id} went back to location step",
            extra={"chat_id": chat_id}
        )

        await UIManager.update(

            chat_id,

            "📍 اضغط على الزر لفتح الخريطة واختيار موقع المحل الحقيقي:",

            location_webapp_ui()
        )

    elif previous == "type":

        logger.info(
            "User {chat_id} went back to type step",
            extra={"chat_id": chat_id}
        )

        await UIManager.update(

            chat_id,

            "🍽️ اختر نوع المحل:",

            types_ui()
        )

    else:

        text, ui = steps_ui[previous]

        logger.info(
            "User {chat_id} went back to {step} step",
            extra={"chat_id": chat_id, "step": previous}
        )

        await UIManager.update(

            chat_id,

            message_id,

            text,

            ui
        )
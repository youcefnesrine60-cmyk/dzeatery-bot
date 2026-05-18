#================================================
# المسؤول عن:
# /start
# الرجوع
# توجيه الرسائل حسب الـ state
#=================================================

from app.services.telegram_service import (
    delete_message
)

from app.helpers.ui_manager import (
    UIManager
)

from app.repositories.state_repo import (
    get_state,
    delete_state
)

from app.helpers.navigation import (
    go_back
)

from app.helpers.message import (
    send_main_menu
)

from app.views.ui import (
    main_menu_ui
)

from app.views.texts import (
    WELCOME_MESSAGE
)

from app.core.security.captcha_manager import (
    CaptchaManager
)

from app.handlers.captcha_handler import (
    handle_captcha
)

from app.states.owner_states import (
    OwnerStates
)

from app.core.state_dispatcher import (
    StateDispatcher
)

from app.core.logger import (
    logger
)

# =====================================================
# 💬 MESSAGE ROUTER
# =====================================================

async def handle_message(
    data: dict
) -> None:
    
    message = data["message"]

    chat_id = message["chat"]["id"]

    text = message.get("text", "").strip()

    # ==============================================
    # CAPTCHA
    # ==============================================

    captcha_required = await CaptchaManager.is_required(
        chat_id
    )

    if captcha_required:

        logger.info(
            "captcha_required",
            extra={
                "chat_id": chat_id
            }
        )

        solved = await handle_captcha(

            chat_id,

            text
        )

        if not solved:

            logger.warning(

                "captcha_failed",

                extra={
                    "chat_id": chat_id
                }
            )

            return

    # =================================================
    # 🚀 START
    # =================================================

    if text == "/start":

        logger.info(
            "start_command",

            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(
            chat_id, 
            WELCOME_MESSAGE,
            main_menu_ui()
        )

        return

    # =================================================
    # 🔙 BACK BUTTON
    # =================================================

    if text == "🔙 رجوع":

        previous = go_back(chat_id)

        if not previous:

            logger.info(
                "back_button_pressed",
                extra={
                    "chat_id": chat_id
                }
            )

            try:
                delete_state(chat_id)
                logger.info(
                    "state_deleted_on_back",
                    extra={
                        "chat_id": chat_id
                    }
                )
            except Exception as e:
                logger.exception(
                    "state_cleanup_failed",
                    extra={
                        "chat_id": chat_id,
                        "error": str(e)
                    }
                )

            await send_main_menu(chat_id)

        return

    # =================================================
    # 🧠 USER STATE FLOW
    # =================================================

    state = get_state(chat_id)

    if not state:

        logger.info(
            "no_state_message",
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )
        return

    # =============================================
    # 🚫 PREVENT MANUAL TEXT IN BUTTON STEPS
    # منع الكتابة أثناء مراحل الأزرار
    # =============================================

    if state.get("step") in [

        OwnerStates.TYPE,

        OwnerStates.CONFIRM
    ]:
        logger.warning(
            "manual_text_in_button_step",
            extra={
                "chat_id": chat_id,
                "step": state.get("step"),
                "text": text
            }
        )

        await delete_message(
            chat_id,
            message["message_id"]
        )

        logger.warning(
            "manual_text_in_button_step",
            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(
            chat_id,
            "❌ الرجاء استعمال الأزرار فقط."
        )

        return
    
    # ==========================================
    # DISPATCH TO STATE HANDLER
    # ==========================================

    await StateDispatcher.dispatch(

        chat_id,

        text,

        state
    )
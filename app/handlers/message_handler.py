# ==============================================
# 💬 MESSAGE HANDLER - VERSION PRO -
# ==============================================

from app.core.logger import logger
from app.core.state_dispatcher import StateDispatcher
from app.core.security.captcha_manager import CaptchaManager
from app.handlers.captcha_handler import handle_captcha
from app.helpers.ui_helpers import send_main_menu
from app.helpers.navigation import go_back
from app.helpers.state_helper import append_to_state_list
from app.helpers.ui_manager import UIManager
from app.repositories.state_repo import delete_state, get_state
from app.services.telegram import delete_message
from app.states.owner_states import OwnerStates


# ==============================================
# 💬 HANDLE MESSAGE
# ==============================================

async def handle_message(
    *,
    data: dict,
) -> None:

    message = data["message"]
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    text = message.get("text", "").strip()

    logger.info(
        "message_received",
        extra={
            "chat_id": chat_id,
            "text_length": len(text),
        },
    )

    # ==========================================
    # 🤖 CAPTCHA VERIFICATION
    # ==========================================

    if await CaptchaManager.is_required(chat_id=chat_id):
        solved = await handle_captcha(
            chat_id=chat_id,
            text=text,
        )
        if not solved:
            return

    # ==========================================
    # 🚀 START COMMAND
    # ==========================================

    if text == "/start":
        logger.info(
            "start_command",
            extra={
                "chat_id": chat_id,
            },
        )

        await UIManager.cleanup_messages(chat_id=chat_id)

        await send_main_menu(
            chat_id=chat_id,
            message_id=None,
            cleanup=False,
        )
        return

    # ==========================================
    # 🔙 BACK BUTTON
    # ==========================================

    if text == "🔙 رجوع":
        logger.info(
            "back_requested",
            extra={
                "chat_id": chat_id,
            },
        )

        previous = await go_back(chat_id=chat_id)

        if previous is None:
            try:
                await delete_state(chat_id=chat_id)
            except Exception as e:
                logger.exception(
                    "state_cleanup_failed",
                    extra={
                        "chat_id": chat_id,
                        "error": str(e),
                    },
                )

            await UIManager.cleanup_messages(chat_id=chat_id)

            await send_main_menu(
                chat_id=chat_id,
                message_id=None,
                cleanup=False,
            )
        return

    # ==========================================
    # 📥 LOAD USER STATE
    # ==========================================

    state = await get_state(chat_id=chat_id)

    if not state:
        logger.info(
            "state_not_found",
            extra={
                "chat_id": chat_id,
            },
        )
        return

    # ==========================================
    # 💾 STORE USER MESSAGE ID (قبل التوجيه)
    # ==========================================

    await append_to_state_list(
        chat_id=chat_id,
        list_key="message_ids",
        value=message_id,
    )

    logger.debug(
        "user_message_id_stored",
        extra={
            "chat_id": chat_id,
            "message_id": message_id,
        },
    )

    # ==========================================
    # 🚫 PREVENT MANUAL INPUT
    # ==========================================

    if state.get("step") in (
        OwnerStates.TYPE,
        OwnerStates.CONFIRM,
    ):
        logger.warning(
            "manual_text_in_button_step",
            extra={
                "chat_id": chat_id,
                "step": state["step"],
            },
        )

        await delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )

        await UIManager.edit(
            chat_id=chat_id,
            message_id=message_id,
            text="❌ الرجاء استعمال الأزرار فقط.",
            reply_markup=None,
        )
        return

    # ==========================================
    # 🚀 DISPATCH STATE
    # ==========================================

    logger.info(
        "state_dispatch_started",
        extra={
            "chat_id": chat_id,
            "step": state.get("step"),
        },
    )

    await StateDispatcher.dispatch(
        chat_id=chat_id,
        text=text,
        state=state,
        message_id=message_id,
    )
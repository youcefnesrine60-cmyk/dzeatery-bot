# ============================================
# 🤖 TELEGRAM CLIENT
# ============================================

from app.core.logger import logger
from app.services.telegram.base import _post
from app.services.telegram.constants import PARSE_MODE


# ============================================
# 🧩 TYPES
# ============================================

TelegramResponse = dict | None
ReplyMarkup = dict | None


# ============================================
# 💬 SEND MESSAGE
# ============================================

async def send_message(
    *,
    chat_id: int,
    text: str,
    reply_markup: ReplyMarkup = None
) -> TelegramResponse:

    logger.info(
        "sending_message",
        extra={
            "chat_id": chat_id
        }
    )

    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": PARSE_MODE,
        "disable_web_page_preview": True
    }

    # ========================================
    # 🎛️ REPLY MARKUP
    # ========================================

    if reply_markup is not None:

        logger.debug(
            "sending_message_with_reply_markup",
            extra={
                "chat_id": chat_id
            }
        )

        data["reply_markup"] = reply_markup

    logger.debug(
        "send_message_payload_prepared",
        extra={
            "chat_id": chat_id
        }
    )

    return await _post(
        method="sendMessage",
        data=data
    )


# ============================================
# ✏️ EDIT MESSAGE
# ============================================

async def edit_message(
    *,
    chat_id: int,
    message_id: int,
    text: str,
    reply_markup: ReplyMarkup = None
) -> TelegramResponse:

    logger.info(
        "editing_message",
        extra={
            "chat_id": chat_id,
            "message_id": message_id
        }
    )

    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": PARSE_MODE,
        "disable_web_page_preview": True
    }

    # ========================================
    # 🎛️ REPLY MARKUP
    # ========================================

    if reply_markup is not None:

        logger.debug(
            "editing_message_with_reply_markup",
            extra={
                "chat_id": chat_id,
                "message_id": message_id
            }
        )

        data["reply_markup"] = reply_markup

    logger.debug(
        "edit_message_payload_prepared",
        extra={
            "chat_id": chat_id,
            "message_id": message_id
        }
    )

    return await _post(
        method="editMessageText",
        data=data
    )


# ============================================
# 🗑️ DELETE MESSAGE
# ============================================

async def delete_message(
    *,
    chat_id: int,
    message_id: int
) -> TelegramResponse:

    logger.info(
        "deleting_message",
        extra={
            "chat_id": chat_id,
            "message_id": message_id
        }
    )

    return await _post(
        method="deleteMessage",
        data={
            "chat_id": chat_id,
            "message_id": message_id
        }
    )
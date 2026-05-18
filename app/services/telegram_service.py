import httpx

from app.config import BOT_TOKEN
from app.core.logger import logger


BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ============================================
# 🌐 HTTP CLIENT
# ============================================

client = httpx.AsyncClient(
    timeout=20.0
)


# ============================================
# 📡 BASE REQUEST
# ============================================

async def _post(
    method: str,
    data: dict
) -> dict | None:

    try:

        response = await client.post(

            f"{BASE_URL}/{method}",

            json=data
        )

        result = response.json()

        # ======================================
        # 🚫 TELEGRAM API ERROR
        # ======================================

        if not result.get("ok"):

            logger.error(

                "telegram_api_error",

                extra={
                    "method": method,
                    "response": result
                }
            )

        return result

    except Exception as e:

        logger.exception(

            "telegram_request_failed",

            extra={
                "method": method,
                "error": str(e)
            }
        )

        return None


# ============================================
# 💬 SEND MESSAGE
# ============================================

async def send_message(
    chat_id: int,
    text: str,
    reply_markup: dict | None = None
) -> dict | None:

    data = {

        "chat_id": chat_id,

        "text": text,

        "parse_mode": "HTML",

        "disable_web_page_preview": True
    }

    if reply_markup:

        data["reply_markup"] = reply_markup

    return await _post(
        "sendMessage",
        data
    )


# ============================================
# ✏️ EDIT MESSAGE
# ============================================

async def edit_message(
    chat_id: int,
    message_id: int,
    text: str,
    reply_markup: dict | None = None
) -> dict | None:

    data = {

        "chat_id": chat_id,

        "message_id": message_id,

        "text": text,

        "parse_mode": "HTML",

        "disable_web_page_preview": True
    }

    if reply_markup:

        data["reply_markup"] = reply_markup

    return await _post(
        "editMessageText",
        data
    )


# ============================================
# 🗑️ DELETE MESSAGE
# ============================================

async def delete_message(
    chat_id: int,
    message_id: int
) -> dict | None:

    return await _post(

        "deleteMessage",

        {
            "chat_id": chat_id,
            "message_id": message_id
        }
    )


# ============================================
# ☑️ ANSWER CALLBACK
# ============================================

async def answer_callback(
    callback_id: str
) -> dict | None:

    return await _post(

        "answerCallbackQuery",

        {
            "callback_query_id": callback_id
        }
    )


# ============================================
# 🔗 SET WEBHOOK
# ============================================

async def set_webhook(
    url: str
) -> dict | None:

    logger.info(

        "setting_webhook",

        extra={
            "url": url
        }
    )

    return await _post(

        "setWebhook",

        {
            "url": url
        }
    )

# ============================================
# SEND CHAT ACTION
# ============================================

async def send_typing(

    chat_id: int,

    action: str = "typing"
) -> dict | None:

    return await _post(

        "sendChatAction",

        {
            "chat_id": chat_id,
            "action": action
        }
    )
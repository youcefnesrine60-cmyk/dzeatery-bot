# ============================================
# 🤖 TELEGRAM API SERVICE
# ============================================

import httpx

from app.config import (
    BOT_TOKEN
)

from app.core.logger import (
    logger
)

# ============================================
# 🌐 BASE URL
# ============================================

BASE_URL = (

    f"https://api.telegram.org/bot{BOT_TOKEN}"
)

# ============================================
# 🌐 HTTP CLIENT
# ============================================

client = httpx.AsyncClient(

    timeout=httpx.Timeout(20.0),

    limits=httpx.Limits(

        max_keepalive_connections=20,

        max_connections=100
    )
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

        # ======================================
        # 🚫 HTTP ERROR
        # ======================================

        response.raise_for_status()

        # ======================================
        # 📦 JSON
        # ======================================

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

            return None

        # ======================================
        # ✅ SUCCESS
        # ======================================

        logger.info(

            "telegram_api_success",

            extra={
                "method": method
            }
        )

        return result

    # ==========================================
    # 🚫 HTTP ERROR
    # ==========================================

    except httpx.HTTPStatusError as e:

        logger.exception(

            "telegram_http_error",

            extra={
                "method": method,
                "status_code": e.response.status_code
            }
        )

        return None

    # ==========================================
    # 🚫 REQUEST ERROR
    # ==========================================

    except httpx.RequestError as e:

        logger.exception(

            "telegram_request_error",

            extra={
                "method": method,
                "error": str(e)
            }
        )

        return None

    # ==========================================
    # 🚫 UNKNOWN ERROR
    # ==========================================

    except Exception as e:

        logger.exception(

            "telegram_unknown_error",

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
# ⌨️ SEND TYPING
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

# ============================================
# ❌ CLOSE HTTP CLIENT
# ============================================

async def close_http_client() -> None:

    await client.aclose()

    logger.info(
        "telegram_http_client_closed"
    )
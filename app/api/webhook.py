# ==============================================
#           🔵 GLOBAL ENTRY POINT 🔵
# ==============================================

from fastapi import (

    APIRouter,

    Request
)

from app.core.dispatcher import (
    dispatch_update
)

from app.core.middleware.gateway import (
    GatewayMiddleware
)

from app.core.middleware.request_logger import (
    RequestLogger
)

from app.handlers.callback_routes import (
    setup_routes
)

from app.core.security.risk_engine import (
    RiskEngine
)

from app.core.logger import (
    logger
)

# ==============================================
# 🚀 API ROUTER
# ==============================================

router = APIRouter()

# ==============================================
# 🚀 REGISTER CALLBACK ROUTES
# ==============================================

setup_routes()

# ==============================================
# 🚀 WEBHOOK ENDPOINT
# ==============================================

@router.post("/webhook")

async def telegram_webhook(

    *,

    request: Request

) -> dict:

    # ==========================================
    # 📦 REQUEST DATA
    # ==========================================

    data = await request.json()

    # ==========================================
    # 🔍 DEFAULT VALUES
    # ==========================================

    chat_id = None

    update_type = "unknown"

    text = None

    # ==========================================
    # 💬 MESSAGE UPDATE
    # ==========================================

    if "message" in data:

        message = data["message"]

        chat_id = message["chat"]["id"]

        text = message.get("text")

        update_type = "message"

        logger.info(

            "received_message",

            extra={
                "chat_id": chat_id,
                "text_length": len(text) if text else 0
            }
        )

    # ==========================================
    # 🔘 CALLBACK UPDATE
    # ==========================================

    elif "callback_query" in data:

        callback = data["callback_query"]

        chat_id = callback["message"]["chat"]["id"]

        update_type = "callback"

        logger.info(

            "received_callback",

            extra={
                "chat_id": chat_id
            }
        )

    # ==========================================
    # 🚫 INVALID UPDATE
    # ==========================================

    if not chat_id:

        logger.warning(

            "webhook_missing_chat_id"
        )

        return {
            "ok": False
        }

    # ==========================================
    # 📜 REQUEST LOGGER
    # ==========================================

    logger.info(

        "logging_request",

        extra={
            "chat_id": chat_id,
            "update_type": update_type
        }
    )

    await RequestLogger.log(

        chat_id = chat_id,

        update_type = update_type
    )

    # ==========================================
    # 🌍 GATEWAY CHECK
    # ==========================================

    logger.info(

        "gateway_check",

        extra={
            "chat_id": chat_id
        }
    )

    allowed = await GatewayMiddleware.process(

        chat_id = chat_id
    )

    if not allowed:

        logger.warning(

            "gateway_blocked",

            extra={
                "chat_id": chat_id
            }
        )

        return {
            "ok": False
        }

    # ==========================================
    # 🛡️ RISK ANALYSIS
    # ==========================================

    logger.info(

        "risk_analysis",

        extra={
            "chat_id": chat_id,
            "text_length": len(text) if text else 0
        }
    )

    safe = await RiskEngine.analyze(

        chat_id = chat_id,

        text = text
    )

    if not safe:

        logger.warning(

            "risk_blocked",

            extra={
                "chat_id": chat_id
            }
        )

        return {
            "ok": False
        }

    # ==========================================
    # 🚀 DISPATCH UPDATE
    # ==========================================

    logger.info(

        "dispatching_update",

        extra={
            "chat_id": chat_id,
            "update_type": update_type
        }
    )

    await dispatch_update(

        data = data
    )

    # ==========================================
    # ✅ SUCCESS
    # ==========================================

    return {
        "ok": True
    }
# ==============================================
#           🔵 Global Entry Point 🔵
# ==============================================

from fastapi import (

    APIRouter,

    Request
)

from app.core.dispatcher import dispatch_update

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
# 🚀 WEBHOOK ENDPOINT (🌍 TELEGRAM WEBHOOK)
# ==============================================

@router.post("/webhook")

async def telegram_webhook(

    request: Request
) -> dict:

    # ==========================================
    # REQUEST
    # ==========================================

    data = await request.json()

    # ======================================
    # EXTRACT CHAT ID
    # ======================================

    chat_id = None

    update_type = "unknown"

    text = None

    if "message" in data:

        chat_id = data["message"]["chat"]["id"]

        logger.info(
            "received_message",
            extra={
                "chat_id": data["message"]["chat"]["id"],
                "text": data["message"].get("text", "")
            }
        )

        text = data["message"].get("text")

        update_type = "message"

    elif "callback_query" in data:

        logger.info(
            "received_callback",
            extra={
                "chat_id": data["callback_query"]["message"]["chat"]["id"]
            }
        )

        chat_id = data["callback_query"]["message"]["chat"]["id"]

        update_type = "callback"

    # ======================================
    # 📜 REQUEST LOGGER
    # ======================================

    if chat_id:

        logger.info(
            "logging_request",
            extra={
                "chat_id": chat_id,
                "update_type": update_type
            }
        )

        await RequestLogger.log(

            chat_id,

            update_type
        )

    # ======================================
    # 🌍 GATEWAY MIDDLEWARE
    # ======================================

    if chat_id:

        logger.info(
            "gateway_check",
            extra={
                "chat_id": chat_id
            }
        )

        allowed = await GatewayMiddleware.process(

            chat_id
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

    # ======================================
    # 🛡️ RISK ENGINE
    # ======================================

    if chat_id:

        logger.info(
            "risk_analysis",
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        safe = await RiskEngine.analyze(

            chat_id,
            text
        )

        if not safe:

            logger.warning(
                "risk_blocked",
                extra={
                    "chat_id": chat_id,
                    "text": text
                }
            )

            return {
                "ok": False
            }

    # ======================================
    # 🚀 DISPATCH UPDATE
    # ======================================

    logger.info(
        "dispatching_update",
        extra={
            "chat_id": chat_id
        }
    )

    await dispatch_update(data)

    return {
        "ok": True
    }
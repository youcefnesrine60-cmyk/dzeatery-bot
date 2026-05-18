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

    if "message" in data:

        chat_id = data["message"]["chat"]["id"]

        update_type = "message"

    elif "callback_query" in data:

        chat_id = data["callback_query"]["message"]["chat"]["id"]

        update_type = "callback"

    # ======================================
    # 📜 REQUEST LOGGER
    # ======================================

    if chat_id:

        await RequestLogger.log(

            chat_id,

            update_type
        )

    # ======================================
    # 🌍 GATEWAY MIDDLEWARE
    # ======================================

    if chat_id:

        allowed = await GatewayMiddleware.process(

            chat_id
        )

        if not allowed:

            return {
                "ok": False
            }

    # ======================================
    # 🛡️ RISK ENGINE
    # ======================================

    if chat_id:

        safe = await RiskEngine.analyze(

            chat_id
        )

        if not safe:

            return {
                "ok": False
            }

    # ======================================
    # 🚀 DISPATCH UPDATE
    # ======================================

    await dispatch_update(data)

    return {
        "ok": True
    }
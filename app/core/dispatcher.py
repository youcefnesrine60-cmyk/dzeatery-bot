from app.core.logger import logger

from app.handlers.callback_handler import (
    handle_callback
)

from app.handlers.message_handler import (
    handle_message
)

from app.handlers.webapp_handler import (
    handle_webapp_data
)


# ==========================================
# 🚀 MAIN UPDATE DISPATCHER
# ==========================================

async def dispatch_update(
        data: dict
) -> None:

    try:

        # ======================================
        # 📌 CALLBACK QUERY
        # ======================================

        if "callback_query" in data:

            await handle_callback(data)

            return

        # ======================================
        # 💬 MESSAGE
        # ======================================

        if "message" in data:

            message = data["message"]

            # ==================================
            # 🌍 WEBAPP DATA
            # ==================================

            if "web_app_data" in message:

                await handle_webapp_data(data)

                return

            await handle_message(data)

    except Exception as e:

        logger.exception(

            "update_dispatch_failed",

            extra={
                "error": str(e)
            }
        )
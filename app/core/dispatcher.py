# ==============================================
# 🚀 MAIN UPDATE DISPATCHER
# ==============================================

from app.handlers.callback_handler import (
    handle_callback
)

from app.handlers.message_handler import (
    handle_message
)

from app.handlers.webapp_handler import (
    handle_webapp_data
)

from app.core.logger import (
    logger
)

# ==============================================
# 🚀 DISPATCH UPDATE
# ==============================================

async def dispatch_update(

    *,

    data: dict

) -> None:

    try:

        # ======================================
        # 📌 CALLBACK QUERY
        # ======================================

        if "callback_query" in data:

            logger.info(

                "dispatching_callback",

                extra={}
            )

            await handle_callback(

                data = data
            )

            return

        # ======================================
        # 💬 MESSAGE
        # ======================================

        if "message" in data:

            message = data["message"]

            logger.info(

                "dispatching_message",

                extra={}
            )

            # ==================================
            # 🌍 WEBAPP DATA
            # ==================================

            if "web_app_data" in message:

                logger.info(

                    "dispatching_webapp_data",

                    extra={}
                )

                await handle_webapp_data(

                    data = data
                )

                return

            # ==================================
            # 💬 NORMAL MESSAGE
            # ==================================

            await handle_message(

                data = data
            )

    except Exception as e:

        logger.exception(

            "update_dispatch_failed",

            extra={

                "error": str(e)
            }
        )
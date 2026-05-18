# ==============================================
# 📌 MAIN CALLBACK DISPATCHER
# ==============================================

from app.core.router_instance import (
    router
)

from app.services.telegram_service import (
    answer_callback
)

from app.core.logger import logger

# ==============================================
# 📌 HANDLE CALLBACK
# ==============================================

async def handle_callback(
    data: dict
) -> None:

    try:

        query = data["callback_query"]

        chat_id = query["message"]["chat"]["id"]

        message_id = query["message"]["message_id"]

        callback_data = query["data"]

        await answer_callback(
            query["id"]
        )

        logger.info(

            "callback_received",

            extra={

                "chat_id": chat_id,

                "event": "callback",

                "order_id": "-"
            }
        )

        await router.dispatch(

            callback_data,

            chat_id,

            message_id
        )

    except Exception as e:

        logger.exception(

            str(e),

            extra={

                "chat_id": chat_id if 'chat_id' in locals() else "-",

                "event": "callback_handler_failed",

                "order_id": "-"
            }
        )
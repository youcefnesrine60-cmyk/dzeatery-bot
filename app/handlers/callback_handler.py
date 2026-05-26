# ==============================================
# 📌 MAIN CALLBACK DISPATCHER
# ==============================================

from app.core.router_instance import (
    router
)

from app.services.telegram import (
    answer_callback
)

from app.core.logger import (
    logger
)

# ==============================================
# 📌 HANDLE CALLBACK
# ==============================================

async def handle_callback(

    *,

    data: dict

) -> None:

    try:

        # ======================================
        # 📦 EXTRACT CALLBACK QUERY
        # ======================================

        query = data["callback_query"]

        chat_id = query["message"]["chat"]["id"]

        message_id = query["message"]["message_id"]

        callback_data = query["data"]

        callback_id = query["id"]

        # ======================================
        # 📥 CALLBACK RECEIVED
        # ======================================

        logger.info(

            "callback_received",

            extra={

                "chat_id": chat_id,

                "callback_data": callback_data
            }
        )

        # ======================================
        # ☑️ ANSWER CALLBACK
        # ======================================

        await answer_callback(

            callback_id = callback_id
        )

        logger.info(

            "callback_answered",

            extra={

                "chat_id": chat_id,

                "callback_data": callback_data
            }
        )

        # ======================================
        # 🚀 DISPATCH CALLBACK
        # ======================================

        await router.dispatch(

            callback_data,

            chat_id,

            message_id
        )

        # ======================================
        # ✅ CALLBACK DISPATCHED
        # ======================================

        logger.info(

            "callback_dispatched",

            extra={

                "chat_id": chat_id,

                "callback_data": callback_data
            }
        )

    # ==========================================
    # 🚫 HANDLE ERRORS
    # ==========================================

    except Exception as e:

        logger.exception(

            "callback_handler_failed",

            extra={

                "chat_id": chat_id if "chat_id" in locals() else None,

                "error": str(e)
            }
        )
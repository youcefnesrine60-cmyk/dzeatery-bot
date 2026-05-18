# ==============================================
# 🍔 RESTAURANT CALLBACKS
# ==============================================

import re

from app.handlers.customer_handler import (
    handle_restaurant_selection
)

from app.core.logger import (
    logger
)

async def restaurant_callback(
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    logger.info(
        "Handling restaurant callback for user {chat_id}",
        extra={
            "chat_id": chat_id, 
            "callback_data": callback_data
        }
    )

    await handle_restaurant_selection(

        chat_id,

        message_id,

        callback_data
    )
import re

from app.core.middleware.rate_limit import (
    rate_limit
)

from app.core.logger import (
    logger
)

@rate_limit(
    limit=5,
    window=20,
    key_prefix="orders"
)

async def order_callback(
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    order_id = match.group(1)

    logger.info(f"User {chat_id} selected order: {order_id}")
# ============================================
# ⌨️ SEND CHAT ACTION
# ============================================

from app.core.logger import (
    logger
)

from app.services.telegram.base import (
    _post
)

async def send_typing(

    chat_id: int,

    action: str = "typing"

) -> dict | None:

    logger.info(

        "sending_chat_action",

        extra={
            "chat_id": chat_id,
            "action": action
        }
    )

    return await _post(

        "sendChatAction",

        {
            "chat_id": chat_id,
            "action": action
        }
    )
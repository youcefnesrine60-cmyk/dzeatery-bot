# ============================================
# ☑️ ANSWER CALLBACK
# ============================================

from app.core.logger import (
    logger
)

from app.services.telegram.base import (
    _post
)


async def answer_callback(

    callback_id: str

) -> dict | None:

    logger.info(
        "answering_callback",
        extra={
            "callback_id": callback_id
        }
    )

    return await _post(

        "answerCallbackQuery",

        {
            "callback_query_id": callback_id
        }
    )
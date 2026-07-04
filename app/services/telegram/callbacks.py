# ============================================
# ☑️ ANSWER CALLBACK
# ============================================

from app.core.logger import logger
from app.services.telegram.base import _post

# ============================================
# 🧩 TYPES
# ============================================

TelegramResponse = dict | None

# ============================================
# ☑️ ANSWER CALLBACK
# ============================================

async def answer_callback(
    *,
    callback_id: str,
) -> TelegramResponse:

    # ========================================
    # 📝 LOG REQUEST
    # ========================================

    logger.info(
        "answering_callback",
        extra={
            "callback_id": callback_id
        }
    )

    # ========================================
    # 🚀 CALL TELEGRAM API
    # ========================================

    return await _post(
        method="answerCallbackQuery",
        data={
            "callback_query_id": callback_id
        }
    )
# ============================================
# 🔗 SET WEBHOOK
# ============================================

from app.core.logger import logger
from app.services.telegram.base import _post

# ============================================
# 🧩 TYPES
# ============================================

TelegramResponse = dict | None

# ============================================
# 🔗 SET WEBHOOK
# ============================================

async def set_webhook(
    *,
    url: str,
) -> TelegramResponse:

    # ========================================
    # 📝 LOG REQUEST
    # ========================================

    logger.info(
        "setting_webhook",
        extra={
            "url": url
        }
    )

    # ========================================
    # 🚀 CALL TELEGRAM API
    # ========================================

    return await _post(
        method="setWebhook",
        data={
            "url": url
        }
    )
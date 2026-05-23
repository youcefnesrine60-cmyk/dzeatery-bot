# ============================================
# 🔗 SET WEBHOOK
# ============================================

from venv import logger

from app.services.telegram.base import _post


async def set_webhook(

    url: str

) -> dict | None:

    logger.info(

        "setting_webhook",

        extra={
            "url": url
        }
    )

    return await _post(

        "setWebhook",

        {
            "url": url
        }
    )
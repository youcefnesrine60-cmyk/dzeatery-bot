# ==============================================
# 🚪 GATEWAY MIDDLEWARE
# ==============================================

from app.core.logger import logger

class GatewayMiddleware:

    @staticmethod
    async def process(
        *,
        chat_id: int
    ) -> bool:

        # ======================================
        # TEMPORARY:
        # Redis limiter disabled
        # ======================================

        logger.info(
            "gateway_processed",
            extra={
                "chat_id": chat_id,
            },
        )

        return True
# ==============================================
# 🚪 GATEWAY MIDDLEWARE
# ==============================================

class GatewayMiddleware:

    @staticmethod
    async def process(
        chat_id: int
    ) -> bool:

        # ======================================
        # TEMPORARY:
        # Redis limiter disabled
        # ======================================

        return True
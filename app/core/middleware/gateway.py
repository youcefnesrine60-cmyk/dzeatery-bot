from app.core.limiter.token_bucket import (
    TokenBucket
)

from app.core.limiter.sliding_window import (
    SlidingWindowLimiter
)

from app.helpers.ui_manager import (
    UIManager
)


# ==========================================
# 🚀 GLOBAL API GATEWAY
# ==========================================

class GatewayMiddleware:

    @staticmethod
    async def process(chat_id: int) -> bool:

        # ======================================================
        # 🚫 BURST PROTECTION (burst attacks / هجمات خاطفة)
        # ======================================================

        burst_allowed = await TokenBucket.allow(

            key=f"burst:{chat_id}",

            capacity=15,

            refill_rate=0.5
        )

        if not burst_allowed:

            await UIManager.update(

                chat_id,

                "⚠️ ضغط كبير جدًا، حاول بعد قليل."
            )

            return False

        # ==========================================================
        # 🌍 GLOBAL RATE LIMIT (sustained attacks / هجمات متواصلة)
        # ==========================================================

        allowed = await SlidingWindowLimiter.is_allowed(

            key=f"global:{chat_id}",

            limit=30,

            window=60
        )

        if not allowed:

            await UIManager.update(

                chat_id,

                "⚠️ عدد الطلبات كبير جدًا."
            )

            return False

        return True
# ===================================
# 🚫 FLOOD / SPAM DETECTION
# كشف الفيضانات / البريد العشوائي
# ===================================

from app.core.limiter.sliding_window import SlidingWindowLimiter
from app.core.logger import logger


# ===================================
# 🚫 ANTI SPAM
# ===================================

class AntiSpam:

    PREFIX = "spam"

    LIMIT = 15

    WINDOW = 10

    # ===================================
    # 🚫 CHECK SPAM
    # ===================================

    @classmethod
    async def check(
        cls: type,
        *,
        chat_id: int
    ) -> bool:

        logger.info(
            "checking_for_spam",
            extra={
                "chat_id": chat_id
            }
        )

        allowed = await SlidingWindowLimiter.is_allowed(
            key=f"{cls.PREFIX}:{chat_id}",
            limit=cls.LIMIT,
            window=cls.WINDOW
        )

        if not allowed:

            logger.warning(
                "spam_detected",
                extra={
                    "chat_id": chat_id
                }
            )

        return allowed
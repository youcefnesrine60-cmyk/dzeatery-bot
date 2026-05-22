#=========================================
# كشف السلوك الآلي
# spam clicking   نقرات عشوائية
# robotic intervals   فواصل زمنية آلية
# impossible speed    سرعة مستحيلة
#=========================================

import time

from app.core.redis_client import (
    redis_client
)

from app.core.limiter.sliding_window import (
    SlidingWindowLimiter
)

from app.core.logger import (
    logger
)

class AntiBot:

    PREFIX = "bot"

    FAST_LIMIT = 5

    FAST_WINDOW = 2

    MIN_HUMAN_DELAY = 0.35

    @classmethod
    async def check(
        cls: type, 
        chat_id: int
    ) -> bool:

        # ======================================
        # 🚫 BURST DETECTION
        # ======================================

        allowed = await SlidingWindowLimiter.is_allowed(

            key=f"{cls.PREFIX}:burst:{chat_id}",

            limit=cls.FAST_LIMIT,

            window=cls.FAST_WINDOW
        )

        if not allowed:

            logger.warning(
                "burst_detected",
                extra={
                    "chat_id": chat_id
                }
            )
            return False

        # ======================================
        # 🚫 HUMAN SPEED DETECTION
        # ======================================

        key = f"{cls.PREFIX}:human:{chat_id}"

        now = time.time()

        if not redis_client:
            logger.warning(
                "Redis client is not initialized",
                extra={
                    "chat_id": chat_id
                }
            )
            return True

        last = redis_client.get(key)

        redis_client.setex(key, 10, now)

        if not last:

            return True

        diff = now - float(last)

        if diff < cls.MIN_HUMAN_DELAY:

            logger.warning(
                "human_speed_detected",
                extra={
                    "chat_id": chat_id,
                    "delay": diff
                }
            )
            return False

        return True
#=========================================
# كشف السلوك الآلي
# spam clicking   نقرات عشوائية
# robotic intervals   فواصل زمنية آلية
# impossible speed    سرعة مستحيلة
#=========================================

import time

from app.core.redis_client import r

from app.core.limiter.sliding_window import (
    SlidingWindowLimiter
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

            return False

        # ======================================
        # 🚫 HUMAN SPEED DETECTION
        # ======================================

        key = f"{cls.PREFIX}:human:{chat_id}"

        now = time.time()

        last = r.get(key)

        r.setex(key, 10, now)

        if not last:

            return True

        diff = now - float(last)

        if diff < cls.MIN_HUMAN_DELAY:

            return False

        return True
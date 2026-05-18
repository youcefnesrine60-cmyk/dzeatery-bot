#===================================
# flood / spam detection
# كشف الفيضانات/البريد العشوائي
#===================================

from app.core.limiter.sliding_window import (
    SlidingWindowLimiter
)


class AntiSpam:

    PREFIX = "spam"

    LIMIT = 15

    WINDOW = 10

    @classmethod
    async def check(
        cls: type, 
        chat_id: int
    ) -> bool:

        return await SlidingWindowLimiter.is_allowed(

            key=f"{cls.PREFIX}:{chat_id}",

            limit=cls.LIMIT,

            window=cls.WINDOW
        )
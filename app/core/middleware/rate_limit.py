from functools import wraps

from app.helpers.ui_manager import (
    UIManager
)

from app.core.limiter.sliding_window import (
    SlidingWindowLimiter
)

# ==============================================
# 🚫 RATE LIMIT MIDDLEWARE (DECORATOR)
# ==============================================

def rate_limit(

    limit: int = 5,

    window: int = 10,

    key_prefix: str = "global"

) -> callable:

    def decorator(func: callable) -> callable:

        @wraps(func)

        async def wrapper(

            chat_id: int,
            *args,
            **kwargs
        ) -> bool:

            key = f"{key_prefix}:{chat_id}"

            allowed = await SlidingWindowLimiter.is_allowed(

                key=key,

                limit=limit,

                window=window
            )

            if not allowed:

                await UIManager.update(

                    chat_id,

                    "⚠️ عدد المحاولات كبير، حاول بعد قليل."
                )

                return False

            return await func(

                chat_id,
                *args,
                **kwargs
            )

        return wrapper

    return decorator
from functools import wraps

from app.helpers.ui_manager import (
    UIManager
)

from app.core.limiter.sliding_window import (
    SlidingWindowLimiter
)

from app.core.logger import (
    logger
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

                logger.warning(

                    "rate_limit_exceeded",

                    extra={
                        "chat_id": chat_id
                    }
                )

                await UIManager.update(

                    chat_id=chat_id,

                    text="⚠️ عدد المحاولات كبير، حاول بعد قليل.",
                    
                    reply_markup=None
                )

                return False

            return await func(

                chat_id,
                *args,
                **kwargs
            )

        return wrapper

    return decorator
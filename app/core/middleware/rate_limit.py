# ==============================================
# 🚫 RATE LIMIT DECORATOR
# ==============================================

from collections.abc import Awaitable
from collections.abc import Callable
from functools import wraps
from typing import Any

from app.core.logger import logger
from app.core.limiter.sliding_window import SlidingWindowLimiter
from app.helpers.ui_manager import UIManager

# ==============================================
# 🧩 TYPES
# ==============================================

Handler = Callable[..., Awaitable[Any]]

# ==============================================
# 🚫 RATE LIMIT DECORATOR
# ==============================================

def rate_limit(
    *,
    limit: int = 5,
    window: int = 10,
    key_prefix: str = "global",
) -> Callable[[Handler], Handler]:

    def decorator(
        func: Handler,
    ) -> Handler:

        @wraps(func)
        async def wrapper(
            chat_id: int,
            *args: Any,
            **kwargs: Any,
        ) -> Any:

            # ==================================
            # 🔑 BUILD KEY
            # ==================================

            key = f"{key_prefix}:{chat_id}"

            allowed = await (
                SlidingWindowLimiter.is_allowed(
                    key=key,
                    limit=limit,
                    window=window,
                )
            )

            # ==================================
            # 🚫 RATE LIMITED
            # ==================================

            if not allowed:

                logger.warning(
                    "rate_limit_exceeded",
                    extra={
                        "chat_id": chat_id,
                        "key": key,
                        "limit": limit,
                        "window": window,
                    },
                )

                await UIManager.update(
                    chat_id=chat_id,
                    text="⚠️ عدد المحاولات كبير، حاول بعد قليل.",
                    reply_markup=None,
                )

                return False

            # ==================================
            # ✅ ALLOWED
            # ==================================

            return await func(
                chat_id=chat_id,
                *args,
                **kwargs,
            )

        return wrapper

    return decorator
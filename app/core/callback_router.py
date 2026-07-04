# ==============================================
# 📌 CALLBACK ROUTER
# ==============================================

import re
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

CallbackHandler = Callable[..., Awaitable[Any]]

# ==============================================
# 📌 CALLBACK ROUTER
# ==============================================

class CallbackRouter:

    # ==========================================
    # 🚀 INIT
    # ==========================================

    def __init__(
        self,
    ) -> None:

        self.routes: list[
            tuple[
                re.Pattern[str],
                CallbackHandler,
            ]
        ] = []

    # ==========================================
    # ➕ REGISTER ROUTE
    # ==========================================

    def register(
        self,
        *,
        pattern: str,
        handler: CallbackHandler,
    ) -> None:

        self.routes.append(
            (
                re.compile(pattern),
                handler,
            )
        )

    # ==========================================
    # 📌 DISPATCH CALLBACK
    # ==========================================

    async def dispatch(
        self,
        callback_data: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        # ======================================
        # 🔍 SEARCH MATCHING ROUTE
        # ======================================

        for regex, handler in self.routes:

            match = regex.match(
                callback_data
            )

            if not match:
                continue

            logger.info(
                "callback_route_matched",
                extra={
                    "callback_data": callback_data,
                    "handler": handler.__name__,
                },
            )

            return await handler(
                *args,
                callback_data=callback_data,
                match=match,
                **kwargs,
            )

        # ======================================
        # 🚫 NO ROUTE FOUND
        # ======================================

        logger.warning(
            "callback_route_not_found",
            extra={
                "callback_data": callback_data,
            },
        )

        return None
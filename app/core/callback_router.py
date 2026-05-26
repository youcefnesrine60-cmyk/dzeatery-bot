# ==============================================
# 📌 CALLBACK ROUTER
# ==============================================

import re

from app.core.logger import (
    logger
)

# ==============================================
# 🚀 CALLBACK ROUTER
# ==============================================

class CallbackRouter:

    # ==========================================
    # 🚀 INIT
    # ==========================================

    def __init__(self) -> None:

        self.routes = []

        logger.info(

            "callback_router_initialized"
        )

    # ==========================================
    # ➕ REGISTER ROUTE
    # ==========================================

    def register(

        self,

        pattern: str,

        handler: callable

    ) -> None:

        compiled = re.compile(pattern)

        self.routes.append(

            (compiled, handler)
        )

        logger.info(

            "callback_route_registered",

            extra={

                "pattern": pattern,

                "handler": handler.__name__
            }
        )

    # ==========================================
    # 📌 DISPATCH CALLBACK
    # ==========================================

    async def dispatch(

        self,

        callback_data: str,

        *args,

        **kwargs

    ) -> any:

        # ======================================
        # 🔍 SEARCH MATCHING ROUTE
        # ======================================

        for regex, handler in self.routes:

            match = regex.match(callback_data)

            # ==================================
            # ✅ MATCH FOUND
            # ==================================

            if match:

                logger.info(

                    "callback_route_matched",

                    extra={

                        "callback_data": callback_data,

                        "handler": handler.__name__
                    }
                )

                return await handler(

                    *args,

                    callback_data = callback_data,

                    match = match,

                    **kwargs
                )

        # ======================================
        # 🚫 NO ROUTE FOUND
        # ======================================

        logger.warning(

            "callback_route_not_found",

            extra={

                "callback_data": callback_data
            }
        )

        return None
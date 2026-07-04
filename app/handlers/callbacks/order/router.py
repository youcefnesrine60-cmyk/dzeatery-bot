# ==============================================
# 📦 ORDER ROUTES
# تسجيل مسارات الطلبات
# ==============================================

from app.core.logger import logger
from app.core.router_instance import router

from app.handlers.callbacks.customer.order import order_details_callback


# ==============================================
# 🚀 REGISTER ORDER ROUTES
# ==============================================

async def register_order_routes() -> None:
    """
    تسجيل جميع مسارات الطلبات في الـ Router
    """
    logger.info(
        "registering_order_routes",
    )

    # 📦 تفاصيل الطلب
    router.register(
        pattern=r"^order_details_(\d+)$",
        handler=order_details_callback,
    )

    logger.info(
        "order_routes_registered",
    )
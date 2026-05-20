# ==============================================
# 📌 CALLBACK ROUTES REGISTRATION
# ==============================================

from app.core.router_instance import router

from app.handlers.callbacks.order_callbacks import (
    order_callback
)

from app.handlers.callbacks.customer import (
    register_customer_routes
)

from app.handlers.callbacks.owner import (
    register_owner_routes
)

from app.handlers.callbacks.type_callbacks import (
    type_callback
)

# ==============================================
# 🚀 SETUP ROUTES
# ==============================================

def setup_routes() -> None:

    # ============================================
    # OWNER ROUTES
    # ============================================

    register_owner_routes()

    # ============================================
    # CUSTOMER ROUTES
    # ============================================

    register_customer_routes()

    # ============================================
    # TYPE
    # ============================================

    router.register(
        r"^type_.*",
        type_callback
    )

    # ============================================
    # PREFIX
    # ============================================

    router.register(
        r"^order_(\d+)$",
        order_callback
    )

    router.register(
        r"^product_(\d+)$",
        order_callback
    )

    router.register(
        r"^payment_.*",
        order_callback
    )

    router.register(
        r"^coupon_.*",
        order_callback
    )
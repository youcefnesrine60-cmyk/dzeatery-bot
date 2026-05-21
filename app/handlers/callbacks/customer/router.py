from app.core.router_instance import router

from app.handlers.callbacks.customer.restaurant_list import (
    customer_callback
)

from app.handlers.callbacks.customer.restaurant_details import (
    handle_restaurant_selection
)

# ==============================================
# 📌 REGISTER CUSTOMER ROUTES
# ==============================================

def register_customer_routes():

    # ==========================================
    # CUSTOMER ENTRY
    # ==========================================

    router.register(

        r"^customer$",

        customer_callback
    )

    # ==========================================
    # RESTAURANT DETAILS
    # ==========================================

    router.register(

        r"^rest_(.+)$",

        handle_restaurant_selection
    )
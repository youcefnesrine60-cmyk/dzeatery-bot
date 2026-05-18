from app.core.router_instance import router

from app.handlers.callbacks.customer.restaurant_list import (
    customer_callback
)

# ==============================================
# 📌 REGISTER CUSTOMER ROUTES
# ==============================================

def register_customer_routes():

    router.callback(

        r"^customer$",

        customer_callback
    )
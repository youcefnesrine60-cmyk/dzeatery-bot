# ==============================================
# 📊 RESTAURANT METRICS SERVICE
# ==============================================

from app.repositories.restaurant_metrics_repo import (
    create_restaurant_metrics,
    get_restaurant_metrics,
    increment_products_count,
    decrement_products_count,
    increment_categories_count,
    decrement_categories_count,
    register_order_metrics,
)

# ==============================================
# INIT
# ==============================================

async def initialize_metrics(
    *,
    restaurant_id: int,
) -> None:

    await create_restaurant_metrics(
        restaurant_id=restaurant_id,
    )

# ==============================================
# PRODUCTS
# ==============================================

async def product_created(
    *,
    restaurant_id: int,
) -> None:

    await increment_products_count(
        restaurant_id=restaurant_id,
    )

async def product_deleted(
    *,
    restaurant_id: int,
) -> None:

    await decrement_products_count(
        restaurant_id=restaurant_id,
    )

# ==============================================
# CATEGORIES
# ==============================================

async def category_created(
    *,
    restaurant_id: int,
) -> None:

    await increment_categories_count(
        restaurant_id=restaurant_id,
    )

async def category_deleted(
    *,
    restaurant_id: int,
) -> None:

    await decrement_categories_count(
        restaurant_id=restaurant_id,
    )

# ==============================================
# ORDERS
# ==============================================

async def order_registered(
    *,
    restaurant_id: int,
    order_total: float,
) -> None:

    await register_order_metrics(
        restaurant_id=restaurant_id,
        order_total=order_total,
    )

# ==============================================
# GET
# ==============================================

async def get_metrics(
    *,
    restaurant_id: int,
):

    return await get_restaurant_metrics(
        restaurant_id=restaurant_id,
    )
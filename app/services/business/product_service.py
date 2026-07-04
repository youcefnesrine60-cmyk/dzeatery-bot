# ==============================================
# 🍔 PRODUCT SERVICE
# Business Logic Layer
# ==============================================

from app.core.logger import logger
from app.guards.feature_guard import require_feature

from app.repositories.products_repo import (
    create_product,
    delete_product,
    get_product_by_id,
    get_restaurant_products,
    set_product_availability,
    update_product,
)
from app.services.business.restaurant_metrics_service import (
    product_created,
    product_deleted,
)
from app.services.business.feature_usage_counter_engine import (
    decrease_usage,
    increase_usage,
)

# ==============================================
# 🧩 CONSTANTS
# ==============================================

PRODUCT_FEATURE_ID = 1

# ==============================================
# ➕ CREATE PRODUCT
# ==============================================

async def create_restaurant_product(
    *,
    restaurant_id: int,
    category_id: int,
    name: str,
    description: str | None,
    price: float,
    image_url: str | None = None,
    sort_order: int = 0,
) -> int:

    await require_feature(
        restaurant_id=restaurant_id,
        feature_id=PRODUCT_FEATURE_ID,
    )

    product_id = await create_product(
        restaurant_id=restaurant_id,
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        image_url=image_url,
        sort_order=sort_order,
    )

    await increase_usage(
        restaurant_id=restaurant_id,
        feature_id=PRODUCT_FEATURE_ID,
    )

    await product_created(
        restaurant_id=restaurant_id,
    )

    logger.info(
        "product_created",
        extra={
            "product_id": product_id,
            "restaurant_id": restaurant_id,
        },
    )

    return product_id

# ==============================================
# 🔍 GET PRODUCT
# ==============================================

async def get_product(
    *,
    product_id: int,
) -> dict[str, object] | None:

    return await get_product_by_id(
        product_id=product_id,
    )

# ==============================================
# 🔍 GET RESTAURANT PRODUCTS
# ==============================================

async def get_products(
    *,
    restaurant_id: int,
) -> list[dict[str, object]]:

    return await get_restaurant_products(
        restaurant_id=restaurant_id,
    )

# ==============================================
# ✏️ EDIT PRODUCT
# ==============================================

async def edit_product(
    *,
    product_id: int,
    name: str,
    description: str | None,
    price: float,
    image_url: str | None,
    sort_order: int,
) -> None:

    await update_product(
        product_id=product_id,
        name=name,
        description=description,
        price=price,
        image_url=image_url,
        sort_order=sort_order,
    )

    logger.info(
        "product_updated",
        extra={
            "product_id": product_id,
        },
    )

# ==============================================
# ✅ ENABLE PRODUCT
# ==============================================

async def enable_product(
    *,
    product_id: int,
) -> None:

    await set_product_availability(
        product_id=product_id,
        is_available=True,
    )

    logger.info(
        "product_enabled",
        extra={
            "product_id": product_id,
        },
    )

# ==============================================
# 🚫 DISABLE PRODUCT
# ==============================================

async def disable_product(
    *,
    product_id: int,
) -> None:

    await set_product_availability(
        product_id=product_id,
        is_available=False,
    )

    logger.info(
        "product_disabled",
        extra={
            "product_id": product_id,
        },
    )

# ==============================================
# ❌ DELETE PRODUCT
# ==============================================

async def remove_product(
    *,
    product_id: int,
) -> None:

    product = await get_product_by_id(
        product_id=product_id,
    )

    if not product:
        raise ValueError(
            "product_not_found"
        )

    restaurant_id = int(
        product["restaurant_id"]
    )

    await delete_product(
        product_id=product_id,
    )

    await product_deleted(
        restaurant_id=product["restaurant_id"],
    )

    await decrease_usage(
        restaurant_id=restaurant_id,
        feature_id=PRODUCT_FEATURE_ID,
    )

    logger.info(
        "product_deleted",
        extra={
            "product_id": product_id,
            "restaurant_id": restaurant_id,
        },
    )
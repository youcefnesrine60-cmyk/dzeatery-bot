# ==============================================
# 📂 CATEGORY SERVICE
# Business Logic Layer
# ==============================================

from app.core.logger import logger
from app.guards.feature_guard import require_feature

from app.repositories.categories_repo import (
    create_category,
    delete_category,
    get_category_by_id,
    get_restaurant_categories,
)

from app.services.business.restaurant_metrics_service import (
    category_created,
    category_deleted,
)

from app.services.business.feature_usage_counter_engine import (
    decrease_usage,
    increase_usage,
)

# ==============================================
# 🧩 CONSTANTS
# ==============================================

CATEGORY_FEATURE_ID = 2

# ==============================================
# ➕ CREATE CATEGORY
# ==============================================

async def create_restaurant_category(
    *,
    restaurant_id: int,
    name: str,
    sort_order: int = 0,
) -> int:

    await require_feature(
        restaurant_id=restaurant_id,
        feature_id=CATEGORY_FEATURE_ID,
    )

    category_id = await create_category(
        restaurant_id=restaurant_id,
        name=name,
        sort_order=sort_order,
    )

    await increase_usage(
        restaurant_id=restaurant_id,
        feature_id=CATEGORY_FEATURE_ID,
    )

    await category_created(
        restaurant_id=restaurant_id,
    )

    logger.info(
        "category_created",
        extra={
            "category_id": category_id,
            "restaurant_id": restaurant_id,
        },
    )

    return category_id

# ==============================================
# 🔍 GET CATEGORY
# ==============================================

async def get_category(
    *,
    category_id: int,
) -> dict[str, object] | None:

    return await get_category_by_id(
        category_id=category_id,
    )

# ==============================================
# 🔍 GET RESTAURANT CATEGORIES
# ==============================================

async def get_categories(
    *,
    restaurant_id: int,
) -> list[dict[str, object]]:

    return await get_restaurant_categories(
        restaurant_id=restaurant_id,
    )

# ==============================================
# ❌ DELETE CATEGORY
# ==============================================

async def remove_category(
    *,
    category_id: int,
) -> None:

    category = await get_category_by_id(
        category_id=category_id,
    )

    if not category:
        raise ValueError(
            "category_not_found"
        )

    restaurant_id = int(
        category["restaurant_id"]
    )

    await delete_category(
        category_id=category_id,
    )

    await category_deleted(
        restaurant_id=category["restaurant_id"],
    )

    await decrease_usage(
        restaurant_id=restaurant_id,
        feature_id=CATEGORY_FEATURE_ID,
    )

    logger.info(
        "category_deleted",
        extra={
            "category_id": category_id,
            "restaurant_id": restaurant_id,
        },
    )
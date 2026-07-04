# ==============================================
# 🏢 MULTI RESTAURANT DISCOUNTS REPOSITORY
# Async Psycopg3 Version
# ==============================================

from app.core.db import (
    execute,
    fetch,
    fetchrow,
    insert_returning_id,
)

from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

MultiRestaurantDiscount = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_MULTI_RESTAURANT_DISCOUNT_SELECT = """
SELECT
    id,
    min_restaurants,
    discount_percent
FROM multi_restaurant_discounts
"""

# ==============================================
# 🧩 ROW MAPPER
# ==============================================

def _row_to_discount(
    row,
) -> MultiRestaurantDiscount:

    return {
        "id": row["id"],
        "min_restaurants": row["min_restaurants"],
        "discount_percent": float(
            row["discount_percent"]
        ),
    }


# ==============================================
# ➕ CREATE DISCOUNT
# ==============================================

async def create_multi_restaurant_discount(
    *,
    min_restaurants: int,
    discount_percent: float,
) -> int:

    discount_id = await insert_returning_id(
        """
        INSERT INTO multi_restaurant_discounts
        (
            min_restaurants,
            discount_percent
        )
        VALUES
        (
            %s,
            %s
        )
        RETURNING id
        """,
        min_restaurants,
        discount_percent,
    )

    logger.info(
        "multi_restaurant_discount_created",
        extra={
            "discount_id": discount_id,
            "min_restaurants": min_restaurants,
        },
    )

    return discount_id


# ==============================================
# 🔍 GET DISCOUNT BY ID
# ==============================================

async def get_multi_restaurant_discount_by_id(
    *,
    discount_id: int,
) -> MultiRestaurantDiscount | None:

    row = await fetchrow(
        _MULTI_RESTAURANT_DISCOUNT_SELECT
        + """
        WHERE id = %s
        """,
        discount_id,
    )

    if not row:
        return None

    return _row_to_discount(row)


# ==============================================
# 🔍 GET ALL DISCOUNTS
# ==============================================

async def get_all_multi_restaurant_discounts(
) -> list[MultiRestaurantDiscount]:

    rows = await fetch(
        _MULTI_RESTAURANT_DISCOUNT_SELECT
        + """
        ORDER BY min_restaurants ASC
        """
    )

    return [
        _row_to_discount(row)
        for row in rows
    ]


# ==============================================
# 🔍 GET APPLICABLE DISCOUNT
# ==============================================

async def get_multi_restaurant_discount_for_count(
    *,
    restaurants_count: int,
) -> MultiRestaurantDiscount | None:

    row = await fetchrow(
        _MULTI_RESTAURANT_DISCOUNT_SELECT
        + """
        WHERE min_restaurants <= %s
        ORDER BY min_restaurants DESC
        LIMIT 1
        """,
        restaurants_count,
    )

    if not row:
        return None

    return _row_to_discount(row)


# ==============================================
# 🔍 GET DISCOUNT PERCENT
# ==============================================

async def get_multi_restaurant_discount_percent(
    *,
    restaurants_count: int,
) -> float:

    discount = await get_multi_restaurant_discount_for_count(
        restaurants_count=restaurants_count,
    )

    if not discount:
        return 0.0

    return float(
        discount["discount_percent"]
    )


# ==============================================
# ✏️ UPDATE DISCOUNT
# ==============================================

async def update_multi_restaurant_discount(
    *,
    discount_id: int,
    min_restaurants: int,
    discount_percent: float,
) -> None:

    await execute(
        """
        UPDATE multi_restaurant_discounts
        SET
            min_restaurants = %s,
            discount_percent = %s
        WHERE id = %s
        """,
        min_restaurants,
        discount_percent,
        discount_id,
    )

    logger.info(
        "multi_restaurant_discount_updated",
        extra={
            "discount_id": discount_id,
        },
    )


# ==============================================
# ❌ DELETE DISCOUNT
# ==============================================

async def delete_multi_restaurant_discount(
    *,
    discount_id: int,
) -> None:

    await execute(
        """
        DELETE FROM multi_restaurant_discounts
        WHERE id = %s
        """,
        discount_id,
    )

    logger.info(
        "multi_restaurant_discount_deleted",
        extra={
            "discount_id": discount_id,
        },
    )
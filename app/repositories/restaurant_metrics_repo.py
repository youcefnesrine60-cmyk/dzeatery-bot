# ==============================================
# 📊 RESTAURANT METRICS REPOSITORY
# Async Psycopg3 Version
# ==============================================

from app.core.db import (
    execute,
    fetchrow,
)

from psycopg import AsyncConnection
from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

RestaurantMetrics = dict[str, object]

# ==============================================
# 📥 BASE SELECT
# ==============================================

BASE_SELECT = """
SELECT
    restaurant_id,
    products_count,
    categories_count,
    monthly_orders,
    average_order_value,
    updated_at
FROM restaurant_metrics
"""

# ==============================================
# 🔍 GET METRICS
# ==============================================

async def get_restaurant_metrics(
    *,
    restaurant_id: int,
) -> RestaurantMetrics | None:

    row = await fetchrow(
        f"""
        {BASE_SELECT}
        WHERE restaurant_id = %s
        """,
        restaurant_id,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# ➕ CREATE DEFAULT METRICS
# ==============================================

async def create_restaurant_metrics(
    *,
    restaurant_id: int,
) -> None:

    await execute(
        """
        INSERT INTO restaurant_metrics
        (
            restaurant_id
        )
        VALUES
        (
            %s
        )
        ON CONFLICT (restaurant_id)
        DO NOTHING
        """,
        restaurant_id,
    )

# ==============================================
# 🍔 INCREMENT PRODUCTS
# ==============================================

async def increment_products_count(
    *,
    restaurant_id: int,
    amount: int = 1,
) -> None:

    await execute(
        """
        UPDATE restaurant_metrics
        SET
            products_count = products_count + %s,
            updated_at = NOW()
        WHERE restaurant_id = %s
        """,
        amount,
        restaurant_id,
    )

# ==============================================
# 🍔 DECREMENT PRODUCTS
# ==============================================

async def decrement_products_count(
    *,
    restaurant_id: int,
    amount: int = 1,
) -> None:

    await execute(
        """
        UPDATE restaurant_metrics
        SET
            products_count =
                GREATEST(
                    products_count - %s,
                    0
                ),
            updated_at = NOW()
        WHERE restaurant_id = %s
        """,
        amount,
        restaurant_id,
    )

# ==============================================
# 📂 INCREMENT CATEGORIES
# ==============================================

async def increment_categories_count(
    *,
    restaurant_id: int,
    amount: int = 1,
) -> None:

    await execute(
        """
        UPDATE restaurant_metrics
        SET
            categories_count = categories_count + %s,
            updated_at = NOW()
        WHERE restaurant_id = %s
        """,
        amount,
        restaurant_id,
    )

# ==============================================
# 📂 DECREMENT CATEGORIES
# ==============================================

async def decrement_categories_count(
    *,
    restaurant_id: int,
    amount: int = 1,
) -> None:

    await execute(
        """
        UPDATE restaurant_metrics
        SET
            categories_count =
                GREATEST(
                    categories_count - %s,
                    0
                ),
            updated_at = NOW()
        WHERE restaurant_id = %s
        """,
        amount,
        restaurant_id,
    )

# ==============================================
# 📦 UPDATE ORDER METRICS
# ==============================================

async def register_order_metrics(
    *,
    restaurant_id: int,
    order_total: float,
) -> None:

    await execute(
        """
        UPDATE restaurant_metrics
        SET
            monthly_orders = monthly_orders + 1,
            average_order_value =
            (
                (
                    average_order_value
                    * monthly_orders
                )
                + %s
            )
            /
            (monthly_orders + 1),
            updated_at = NOW()
        WHERE restaurant_id = %s
        """,
        order_total,
        restaurant_id,
    )

    logger.info(
        "restaurant_metrics_order_updated",
        extra={
            "restaurant_id": restaurant_id,
        },
    )

# ==============================================
# 📈 REGISTER ORDER METRICS (TX)
# ==============================================

async def register_order_metrics_tx(
    *,
    conn: AsyncConnection,
    restaurant_id: int,
    order_total: float,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            UPDATE restaurant_metrics
            SET
                orders_count = orders_count + 1,
                total_revenue = total_revenue + %s,
                updated_at = NOW()
            WHERE restaurant_id = %s
            """,
            (
                order_total,
                restaurant_id,
            ),
        )
# ==============================================
# 📦 ORDER ITEMS REPOSITORY
# Async Psycopg3 Version
# ==============================================

from app.core.db import (
    execute,
    fetch,
    fetchrow,
    insert_returning_id,
)

from psycopg import AsyncConnection
from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

OrderItem = dict[str, object]

# ==============================================
# 📥 BASE SELECT
# ==============================================

BASE_SELECT = """
SELECT
    id,
    order_id,
    product_id,
    product_name,
    unit_price,
    quantity,
    total_price,
    created_at
FROM order_items
"""

# ==============================================
# ➕ CREATE ORDER ITEM
# ==============================================

async def create_order_item(
    *,
    order_id: int,
    product_id: int,
    product_name: str,
    unit_price: float,
    quantity: int,
    total_price: float,
) -> int:

    order_item_id = await insert_returning_id(
        """
        INSERT INTO order_items
        (
            order_id,
            product_id,
            product_name,
            unit_price,
            quantity,
            total_price
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        order_id,
        product_id,
        product_name,
        unit_price,
        quantity,
        total_price,
    )

    logger.info(
        "order_item_created",
        extra={
            "order_item_id": order_item_id,
            "order_id": order_id,
        },
    )

    return order_item_id

# ==============================================
# 🔍 GET ORDER ITEM
# ==============================================

async def get_order_item(
    *,
    order_item_id: int,
) -> OrderItem | None:

    row = await fetchrow(
        f"""
        {BASE_SELECT}
        WHERE id = %s
        """,
        order_item_id,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# 🔍 GET ORDER ITEMS
# ==============================================

async def get_order_items(
    *,
    order_id: int,
) -> list[OrderItem]:

    rows = await fetch(
        f"""
        {BASE_SELECT}
        WHERE order_id = %s
        ORDER BY id
        """,
        order_id,
    )

    return [dict(row) for row in rows]

# ==============================================
# 🔢 COUNT ORDER ITEMS
# ==============================================

async def count_order_items(
    *,
    order_id: int,
) -> int:

    row = await fetchrow(
        """
        SELECT COUNT(*) AS total
        FROM order_items
        WHERE order_id = %s
        """,
        order_id,
    )

    return int(row["total"])

# ==============================================
# 💰 GET ORDER SUBTOTAL
# ==============================================

async def get_order_items_subtotal(
    *,
    order_id: int,
) -> float:

    row = await fetchrow(
        """
        SELECT
            COALESCE(
                SUM(total_price),
                0
            ) AS subtotal
        FROM order_items
        WHERE order_id = %s
        """,
        order_id,
    )

    return float(row["subtotal"])

# ==============================================
# ✏️ UPDATE QUANTITY
# ==============================================

async def update_order_item_quantity(
    *,
    order_item_id: int,
    quantity: int,
    total_price: float,
) -> None:

    await execute(
        """
        UPDATE order_items
        SET
            quantity = %s,
            total_price = %s
        WHERE id = %s
        """,
        quantity,
        total_price,
        order_item_id,
    )

    logger.info(
        "order_item_quantity_updated",
        extra={
            "order_item_id": order_item_id,
        },
    )

# ==============================================
# ❌ DELETE ORDER ITEM
# ==============================================

async def delete_order_item(
    *,
    order_item_id: int,
) -> None:

    await execute(
        """
        DELETE FROM order_items
        WHERE id = %s
        """,
        order_item_id,
    )

    logger.info(
        "order_item_deleted",
        extra={
            "order_item_id": order_item_id,
        },
    )

# ==============================================
# ❌ DELETE ORDER ITEMS
# ==============================================

async def delete_order_items(
    *,
    order_id: int,
) -> None:

    await execute(
        """
        DELETE FROM order_items
        WHERE order_id = %s
        """,
        order_id,
    )

    logger.info(
        "order_items_deleted",
        extra={
            "order_id": order_id,
        },
    )

# ==============================================
# 🔒 TX CREATE ORDER ITEM
# ==============================================

async def create_order_item_tx(
    *,
    conn: AsyncConnection,
    order_id: int,
    product_id: int,
    product_name: str,
    unit_price: float,
    quantity: int,
    total_price: float,
) -> int:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            INSERT INTO order_items
            (
                order_id,
                product_id,
                product_name,
                unit_price,
                quantity,
                total_price
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                order_id,
                product_id,
                product_name,
                unit_price,
                quantity,
                total_price,
            ),
        )

        row = await cur.fetchone()

        return int(row[0])

# ==============================================
# 🔒 TX DELETE ORDER ITEM
# ==============================================

async def delete_order_item_tx(
    *,
    conn: AsyncConnection,
    order_item_id: int,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            DELETE FROM order_items
            WHERE id = %s
            """,
            (
                order_item_id,
            ),
        )
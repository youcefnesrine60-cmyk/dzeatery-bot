# ==============================================
# 🎛 ORDER ITEM OPTIONS REPOSITORY
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

OrderItemOption = dict[str, object]

# ==============================================
# 📥 BASE SELECT
# ==============================================

BASE_SELECT = """
SELECT
    id,
    order_item_id,
    option_group_name,
    option_name,
    additional_price,
    created_at
FROM order_item_options
"""

# ==============================================
# ➕ CREATE OPTION
# ==============================================

async def create_order_item_option(
    *,
    order_item_id: int,
    option_group_name: str,
    option_name: str,
    additional_price: float = 0,
) -> int:

    option_id = await insert_returning_id(
        """
        INSERT INTO order_item_options
        (
            order_item_id,
            option_group_name,
            option_name,
            additional_price
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        order_item_id,
        option_group_name,
        option_name,
        additional_price,
    )

    logger.info(
        "order_item_option_created",
        extra={
            "option_id": option_id,
            "order_item_id": order_item_id,
        },
    )

    return option_id

# ==============================================
# 🔍 GET OPTION
# ==============================================

async def get_order_item_option(
    *,
    option_id: int,
) -> OrderItemOption | None:

    row = await fetchrow(
        f"""
        {BASE_SELECT}
        WHERE id = %s
        """,
        option_id,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# 🔍 GET ITEM OPTIONS
# ==============================================

async def get_order_item_options(
    *,
    order_item_id: int,
) -> list[OrderItemOption]:

    rows = await fetch(
        f"""
        {BASE_SELECT}
        WHERE order_item_id = %s
        ORDER BY id
        """,
        order_item_id,
    )

    return [dict(row) for row in rows]

# ==============================================
# 💰 GET OPTIONS TOTAL
# ==============================================

async def get_order_item_options_total(
    *,
    order_item_id: int,
) -> float:

    row = await fetchrow(
        """
        SELECT
            COALESCE(
                SUM(additional_price),
                0
            ) AS total
        FROM order_item_options
        WHERE order_item_id = %s
        """,
        order_item_id,
    )

    return float(row["total"])

# ==============================================
# 🔢 COUNT OPTIONS
# ==============================================

async def count_order_item_options(
    *,
    order_item_id: int,
) -> int:

    row = await fetchrow(
        """
        SELECT COUNT(*) AS total
        FROM order_item_options
        WHERE order_item_id = %s
        """,
        order_item_id,
    )

    return int(row["total"])

# ==============================================
# ❌ DELETE OPTION
# ==============================================

async def delete_order_item_option(
    *,
    option_id: int,
) -> None:

    await execute(
        """
        DELETE FROM order_item_options
        WHERE id = %s
        """,
        option_id,
    )

    logger.info(
        "order_item_option_deleted",
        extra={
            "option_id": option_id,
        },
    )

# ==============================================
# ❌ DELETE ITEM OPTIONS
# ==============================================

async def delete_order_item_options(
    *,
    order_item_id: int,
) -> None:

    await execute(
        """
        DELETE FROM order_item_options
        WHERE order_item_id = %s
        """,
        order_item_id,
    )

    logger.info(
        "order_item_options_deleted",
        extra={
            "order_item_id": order_item_id,
        },
    )

# ==============================================
# 🔒 TX CREATE ORDER ITEM OPTION
# ==============================================

async def create_order_item_option_tx(
    *,
    conn: AsyncConnection,
    order_item_id: int,
    option_group_name: str,
    option_name: str,
    additional_price: float = 0,
) -> int:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            INSERT INTO order_item_options
            (
                order_item_id,
                option_group_name,
                option_name,
                additional_price
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                order_item_id,
                option_group_name,
                option_name,
                additional_price,
            ),
        )

        row = await cur.fetchone()

        return int(row[0])


# ==============================================
# 🔒 TX DELETE ORDER ITEM OPTION
# ==============================================

async def delete_order_item_option_tx(
    *,
    conn: AsyncConnection,
    option_id: int,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            DELETE FROM order_item_options
            WHERE id = %s
            """,
            (
                option_id,
            ),
        )
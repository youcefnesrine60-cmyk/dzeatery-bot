# ==============================================
# 🔢 RESTAURANT ORDER COUNTERS REPOSITORY
# Async Psycopg3 Version
# ==============================================

from psycopg import AsyncConnection

from app.core.db import (
    execute,
    fetchrow,
)

from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

RestaurantOrderCounter = dict[str, object]

# ==============================================
# 📥 BASE SELECT
# ==============================================

BASE_SELECT = """
SELECT
    restaurant_id,
    last_number,
    created_at,
    updated_at
FROM restaurant_order_counters
"""

# ==============================================
# ➕ CREATE COUNTER
# ==============================================

async def create_order_counter(
    *,
    restaurant_id: int,
) -> None:

    await execute(
        """
        INSERT INTO restaurant_order_counters
        (
            restaurant_id,
            last_number
        )
        VALUES
        (
            %s,
            0
        )
        ON CONFLICT (restaurant_id)
        DO NOTHING
        """,
        restaurant_id,
    )

    logger.info(
        "order_counter_created",
        extra={
            "restaurant_id": restaurant_id,
        },
    )

# ==============================================
# 🔍 GET COUNTER
# ==============================================

async def get_order_counter(
    *,
    restaurant_id: int,
) -> RestaurantOrderCounter | None:

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
# 🔢 GET CURRENT NUMBER
# ==============================================

async def get_current_order_number(
    *,
    restaurant_id: int,
) -> int:

    counter = await get_order_counter(
        restaurant_id=restaurant_id,
    )

    if not counter:
        return 0

    return int(
        counter["last_number"]
    )

# ==============================================
# 🔒 INCREMENT COUNTER (TX)
# IMPORTANT:
# Must run inside transaction
# Uses FOR UPDATE
# ==============================================

async def increment_order_counter_tx(
    *,
    conn: AsyncConnection,
    restaurant_id: int,
) -> int:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            SELECT last_number
            FROM restaurant_order_counters
            WHERE restaurant_id = %s
            FOR UPDATE
            """,
            (
                restaurant_id,
            ),
        )

        row = await cur.fetchone()

        if not row:

            await cur.execute(
                """
                INSERT INTO restaurant_order_counters
                (
                    restaurant_id,
                    last_number
                )
                VALUES
                (
                    %s,
                    1
                )
                RETURNING last_number
                """,
                (
                    restaurant_id,
                ),
            )

            created = await cur.fetchone()

            return int(
                created[0]
            )

        next_number = int(
            row[0]
        ) + 1

        await cur.execute(
            """
            UPDATE restaurant_order_counters
            SET
                last_number = %s,
                updated_at = NOW()
            WHERE restaurant_id = %s
            """,
            (
                next_number,
                restaurant_id,
            ),
        )

        return next_number

# ==============================================
# 🏷 GENERATE ORDER NUMBER
# ==============================================

def build_order_number(
    *,
    restaurant_id: int,
    sequence: int,
) -> str:

    return (
        f"RST{restaurant_id}-"
        f"{sequence:06d}"
    )

# ==============================================
# 🔒 GENERATE NEXT ORDER NUMBER (TX)
# ==============================================

async def generate_next_order_number_tx(
    *,
    conn: AsyncConnection,
    restaurant_id: int,
) -> str:

    sequence = await increment_order_counter_tx(
        conn=conn,
        restaurant_id=restaurant_id,
    )

    return build_order_number(
        restaurant_id=restaurant_id,
        sequence=sequence,
    )
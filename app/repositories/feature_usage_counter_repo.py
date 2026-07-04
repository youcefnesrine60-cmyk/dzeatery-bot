# ==============================================
# 📊 FEATURE USAGE COUNTER REPOSITORY
# Async Psycopg3 Version
# ==============================================

from datetime import datetime
from psycopg import AsyncConnection
from psycopg.rows import dict_row

from app.core.db import (
    execute,
    fetchrow,
    insert_returning_id,
)

from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

FeatureUsageCounter = dict[str, object]

# ==============================================
# 🔍 GET COUNTER
# ==============================================

async def get_feature_counter(
    *,
    restaurant_id: int,
    feature_id: int,
    period_year: int | None = None,
    period_month: int | None = None,
) -> FeatureUsageCounter | None:

    row = await fetchrow(
        """
        SELECT
            id,
            restaurant_id,
            feature_id,
            usage_count,
            period_year,
            period_month,
            created_at,
            updated_at
        FROM feature_usage_counters
        WHERE restaurant_id = %s
          AND feature_id = %s
          AND (
                (%s IS NULL AND period_year IS NULL)
                OR period_year = %s
              )
          AND (
                (%s IS NULL AND period_month IS NULL)
                OR period_month = %s
              )
        LIMIT 1
        """,
        restaurant_id,
        feature_id,
        period_year,
        period_year,
        period_month,
        period_month,
    )

    return dict(row) if row else None


# ==============================================
# ➕ CREATE COUNTER
# ==============================================

async def create_feature_counter(
    *,
    restaurant_id: int,
    feature_id: int,
    usage_count: int = 0,
    period_year: int | None = None,
    period_month: int | None = None,
) -> int:

    counter_id = await insert_returning_id(
        """
        INSERT INTO feature_usage_counters
        (
            restaurant_id,
            feature_id,
            usage_count,
            period_year,
            period_month
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        restaurant_id,
        feature_id,
        usage_count,
        period_year,
        period_month,
    )

    logger.info(
        "feature_counter_created",
        extra={
            "counter_id": counter_id,
            "restaurant_id": restaurant_id,
            "feature_id": feature_id,
        },
    )

    return counter_id


# ==============================================
# 📈 INCREMENT COUNTER
# ==============================================

async def increment_feature_counter(
    *,
    counter_id: int,
    amount: int = 1,
) -> None:

    await execute(
        """
        UPDATE feature_usage_counters
        SET
            usage_count = usage_count + %s,
            updated_at = NOW()
        WHERE id = %s
        """,
        amount,
        counter_id,
    )


# ==============================================
# 📉 DECREMENT COUNTER
# ==============================================

async def decrement_feature_counter(
    *,
    counter_id: int,
    amount: int = 1,
) -> None:

    await execute(
        """
        UPDATE feature_usage_counters
        SET
            usage_count =
                GREATEST(
                    usage_count - %s,
                    0
                ),
            updated_at = NOW()
        WHERE id = %s
        """,
        amount,
        counter_id,
    )


# ==============================================
# 🔄 RESET MONTHLY COUNTER
# ==============================================

async def reset_feature_counter(
    *,
    counter_id: int,
) -> None:

    await execute(
        """
        UPDATE feature_usage_counters
        SET
            usage_count = 0,
            updated_at = NOW()
        WHERE id = %s
        """,
        counter_id,
    )


# ==============================================
# 🔍 CURRENT USAGE
# ==============================================

async def get_current_usage(
    *,
    restaurant_id: int,
    feature_id: int,
    period_year: int | None = None,
    period_month: int | None = None,
) -> int:

    counter = await get_feature_counter(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
        period_year=period_year,
        period_month=period_month,
    )

    if not counter:
        return 0

    return int(counter["usage_count"])

# ==============================================
# 🔍 GET FEATURE COUNTER (TX)
# ==============================================

async def get_feature_counter_tx(
    *,
    conn: AsyncConnection,
    restaurant_id: int,
    feature_id: int,
    period_year: int,
    period_month: int,
) -> dict[str, object] | None:

    async with conn.cursor(row_factory=dict_row) as cur:

        await cur.execute(
            """
            SELECT
                id,
                restaurant_id,
                feature_id,
                usage_count,
                period_year,
                period_month,
                created_at,
                updated_at
            FROM feature_usage_counters
            WHERE restaurant_id = %s
            AND feature_id = %s
            AND period_year = %s
            AND period_month = %s
            """,
            (
                restaurant_id,
                feature_id,
                period_year,
                period_month,
            ),
        )

        row = await cur.fetchone()

        if not row:
            return None

        return dict(row)
    
# ==============================================
# 🔒 TX CREATE FEATURE COUNTER
# ==============================================

async def create_feature_counter_tx(
    *,
    conn: AsyncConnection,
    restaurant_id: int,
    feature_id: int,
    usage_count: int,
    period_year: int,
    period_month: int,
) -> int:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            INSERT INTO feature_usage_counters
            (
                restaurant_id,
                feature_id,
                usage_count,
                period_year,
                period_month
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                restaurant_id,
                feature_id,
                usage_count,
                period_year,
                period_month,
            ),
        )

        row = await cur.fetchone()

        return int(row[0])
    
# ==============================================
# 🔒 TX INCREMENT FEATURE COUNTER
# ==============================================

async def increment_feature_counter_tx(
    *,
    conn: AsyncConnection,
    counter_id: int,
    amount: int = 1,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            UPDATE feature_usage_counters
            SET
                usage_count = usage_count + %s,
                updated_at = NOW()
            WHERE id = %s
            """,
            (
                amount,
                counter_id,
            ),
        )
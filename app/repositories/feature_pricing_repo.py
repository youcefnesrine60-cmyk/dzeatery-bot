# ==============================================
# 💰 FEATURE PRICING REPOSITORY
# Async Psycopg3 Version
# ==============================================

from app.core.db import (
    execute, 
    fetch, 
    fetchrow, 
    insert_returning_id
)
from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

FeaturePricing = dict[str, object]

# ==============================================
# 🧩 BASE SELECT
# ==============================================

_FEATURE_PRICING_SELECT = """
SELECT
    id,
    feature_id,
    billing_cycle,
    price,
    active
FROM feature_pricing
"""


def _row_to_feature_pricing(row) -> FeaturePricing:
    return {
        "id": row["id"],
        "feature_id": row["feature_id"],
        "billing_cycle": row["billing_cycle"],
        "price": float(row["price"]),
        "active": row["active"],
    }


# ==============================================
# ➕ CREATE FEATURE PRICING
# ==============================================

async def create_feature_pricing(
    *,
    feature_id: int,
    billing_cycle: str,
    price: float,
    active: bool = True,
) -> int:

    pricing_id = await insert_returning_id(
        """
        INSERT INTO feature_pricing (
            feature_id,
            billing_cycle,
            price,
            active
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        feature_id,
        billing_cycle,
        price,
        active,
    )

    logger.info(
        "feature_pricing_created",
        extra={
            "pricing_id": pricing_id,
            "feature_id": feature_id,
        },
    )

    return pricing_id


# ==============================================
# 🔍 GET FEATURE PRICING BY ID
# ==============================================

async def get_feature_pricing_by_id(
    *,
    pricing_id: int,
) -> FeaturePricing | None:

    row = await fetchrow(
        _FEATURE_PRICING_SELECT + " WHERE id = %s",
        pricing_id,
    )

    return _row_to_feature_pricing(row) if row else None


# ==============================================
# 🔍 GET FEATURE PRICING (BY FEATURE + CYCLE)
# ==============================================

async def get_feature_pricing(
    *,
    feature_id: int,
    billing_cycle: str,
) -> FeaturePricing | None:

    row = await fetchrow(
        _FEATURE_PRICING_SELECT + """
        WHERE feature_id = %s
          AND billing_cycle = %s
          AND active = TRUE
        LIMIT 1
        """,
        feature_id,
        billing_cycle,
    )

    return _row_to_feature_pricing(row) if row else None


# ==============================================
# 🔍 GET FEATURE PRICING LIST
# ==============================================

async def get_feature_pricing_list(
    *,
    feature_id: int,
) -> list[FeaturePricing]:

    rows = await fetch(
        _FEATURE_PRICING_SELECT + """
        WHERE feature_id = %s
        ORDER BY id ASC
        """,
        feature_id,
    )

    return [_row_to_feature_pricing(row) for row in rows]


# ==============================================
# 🔍 GET ALL FEATURE PRICING
# ==============================================

async def get_all_feature_pricing() -> list[FeaturePricing]:

    rows = await fetch(
        _FEATURE_PRICING_SELECT + """
        ORDER BY id ASC
        """
    )

    return [_row_to_feature_pricing(row) for row in rows]


# ==============================================
# ✏️ UPDATE FEATURE PRICE
# ==============================================

async def update_feature_price(
    *,
    pricing_id: int,
    price: float,
) -> None:

    await execute(
        """
        UPDATE feature_pricing
        SET price = %s
        WHERE id = %s
        """,
        price,
        pricing_id,
    )

    logger.info(
        "feature_price_updated",
        extra={
            "pricing_id": pricing_id,
            "price": price,
        },
    )


# ==============================================
# ✅ ACTIVATE FEATURE PRICING
# ==============================================

async def activate_feature_pricing(
    *,
    pricing_id: int,
) -> None:

    await execute(
        """
        UPDATE feature_pricing
        SET active = TRUE
        WHERE id = %s
        """,
        pricing_id,
    )

    logger.info(
        "feature_pricing_activated",
        extra={"pricing_id": pricing_id},
    )


# ==============================================
# ❌ DEACTIVATE FEATURE PRICING
# ==============================================

async def deactivate_feature_pricing(
    *,
    pricing_id: int,
) -> None:

    await execute(
        """
        UPDATE feature_pricing
        SET active = FALSE
        WHERE id = %s
        """,
        pricing_id,
    )

    logger.info(
        "feature_pricing_deactivated",
        extra={"pricing_id": pricing_id},
    )


# ==============================================
# ❌ DELETE FEATURE PRICING
# ==============================================

async def delete_feature_pricing(
    *,
    pricing_id: int,
) -> None:

    await execute(
        """
        DELETE FROM feature_pricing
        WHERE id = %s
        """,
        pricing_id,
    )

    logger.info(
        "feature_pricing_deleted",
        extra={"pricing_id": pricing_id},
    )
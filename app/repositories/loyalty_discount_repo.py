# ==============================================
# 💎 LOYALTY DISCOUNTS REPOSITORY
# مستودع خصومات الولاء
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

LoyaltyDiscount = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_LOYALTY_DISCOUNT_SELECT = """
SELECT
    id,
    years_required,
    discount_percent
FROM loyalty_discounts
"""

# ==============================================
# 🧩 ROW MAPPER
# ==============================================

def _row_to_discount(
    row,
) -> LoyaltyDiscount:

    return {
        "id": row["id"],
        "years_required": row["years_required"],
        "discount_percent": float(
            row["discount_percent"]
        ),
    }


# ==============================================
# ➕ CREATE DISCOUNT
# ==============================================

async def create_loyalty_discount(
    *,
    years_required: int,
    discount_percent: float,
) -> int:

    discount_id = await insert_returning_id(
        """
        INSERT INTO loyalty_discounts
        (
            years_required,
            discount_percent
        )
        VALUES
        (
            %s,
            %s
        )
        RETURNING id
        """,
        years_required,
        discount_percent,
    )

    logger.info(
        "loyalty_discount_created",
        extra={
            "discount_id": discount_id,
            "years_required": years_required,
            "discount_percent": discount_percent,
        },
    )

    return discount_id


# ==============================================
# 🔍 GET BY ID
# ==============================================

async def get_loyalty_discount_by_id(
    *,
    discount_id: int,
) -> LoyaltyDiscount | None:

    row = await fetchrow(
        _LOYALTY_DISCOUNT_SELECT
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

async def get_all_loyalty_discounts(
) -> list[LoyaltyDiscount]:

    rows = await fetch(
        _LOYALTY_DISCOUNT_SELECT
        + """
        ORDER BY years_required ASC
        """
    )

    discounts = [
        _row_to_discount(row)
        for row in rows
    ]

    logger.info(
        "loyalty_discounts_fetched",
        extra={
            "count": len(discounts),
        },
    )

    return discounts


# ==============================================
# 🔍 GET DISCOUNT FOR YEARS
# ==============================================

async def get_loyalty_discount_for_years(
    *,
    years: int,
) -> float:

    row = await fetchrow(
        """
        SELECT discount_percent
        FROM loyalty_discounts
        WHERE years_required <= %s
        ORDER BY years_required DESC
        LIMIT 1
        """,
        years,
    )

    if not row:
        return 0.0

    return float(
        row["discount_percent"]
    )


# ==============================================
# ✏️ UPDATE DISCOUNT
# ==============================================

async def update_loyalty_discount(
    *,
    discount_id: int,
    discount_percent: float,
) -> None:

    await execute(
        """
        UPDATE loyalty_discounts
        SET discount_percent = %s
        WHERE id = %s
        """,
        discount_percent,
        discount_id,
    )

    logger.info(
        "loyalty_discount_updated",
        extra={
            "discount_id": discount_id,
            "discount_percent": discount_percent,
        },
    )


# ==============================================
# ❌ DELETE DISCOUNT
# ==============================================

async def delete_loyalty_discount(
    *,
    discount_id: int,
) -> None:

    await execute(
        """
        DELETE FROM loyalty_discounts
        WHERE id = %s
        """,
        discount_id,
    )

    logger.info(
        "loyalty_discount_deleted",
        extra={
            "discount_id": discount_id,
        },
    )
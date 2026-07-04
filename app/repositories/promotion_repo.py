# ==============================================
# 🎉 PROMOTION REPOSITORY
# Async Psycopg3 Version
# ==============================================

from datetime import datetime

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

Promotion = dict[str, object]

# ==============================================
# ➕ CREATE PROMOTION
# ==============================================

async def create_promotion(
    *,
    name: str,
    discount_percent: float,
    starts_at: datetime,
    expires_at: datetime,
    active: bool = True,
) -> int:

    promotion_id = await insert_returning_id(
        """
        INSERT INTO promotions (
            name,
            discount_percent,
            starts_at,
            expires_at,
            active
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        name,
        discount_percent,
        starts_at,
        expires_at,
        active,
    )

    logger.info(
        "promotion_created",
        extra={
            "promotion_id": promotion_id,
            "promotion_name": name,
        },
    )

    return promotion_id


# ==============================================
# 🔍 BASE SELECT
# ==============================================

_PROMOTION_SELECT = """
SELECT
    id,
    name,
    discount_percent,
    starts_at,
    expires_at,
    active
FROM promotions
"""


def _row_to_dict(row) -> Promotion:
    return {
        "id": row["id"],
        "name": row["name"],
        "discount_percent": float(row["discount_percent"]),
        "starts_at": row["starts_at"],
        "expires_at": row["expires_at"],
        "active": row["active"],
    }


# ==============================================
# 🔍 GET PROMOTION BY ID
# ==============================================

async def get_promotion_by_id(
    *,
    promotion_id: int,
) -> Promotion | None:

    row = await fetchrow(
        _PROMOTION_SELECT + " WHERE id = %s",
        promotion_id,
    )

    if not row:
        logger.warning(
            "promotion_not_found",
            extra={"promotion_id": promotion_id},
        )
        return None

    return _row_to_dict(row)


# ==============================================
# 🔍 GET ACTIVE PROMOTION
# ==============================================

async def get_active_promotion() -> Promotion | None:

    row = await fetchrow(
        _PROMOTION_SELECT + """
        WHERE active = TRUE
        ORDER BY id DESC
        LIMIT 1
        """
    )

    return _row_to_dict(row) if row else None


# ==============================================
# 📥 GET ALL PROMOTIONS
# ==============================================

async def get_all_promotions() -> list[Promotion]:

    rows = await fetch(
        _PROMOTION_SELECT + """
        ORDER BY id DESC
        """
    )

    promotions = [_row_to_dict(row) for row in rows]

    logger.info(
        "promotions_fetched",
        extra={"count": len(promotions)},
    )

    return promotions


# ==============================================
# ✅ ACTIVATE PROMOTION
# ==============================================

async def activate_promotion(
    *,
    promotion_id: int,
) -> None:

    await execute(
        """
        UPDATE promotions
        SET active = TRUE
        WHERE id = %s
        """,
        promotion_id,
    )

    logger.info(
        "promotion_activated",
        extra={"promotion_id": promotion_id},
    )


# ==============================================
# ❌ DEACTIVATE PROMOTION
# ==============================================

async def deactivate_promotion(
    *,
    promotion_id: int,
) -> None:

    await execute(
        """
        UPDATE promotions
        SET active = FALSE
        WHERE id = %s
        """,
        promotion_id,
    )

    logger.info(
        "promotion_deactivated",
        extra={"promotion_id": promotion_id},
    )


# ==============================================
# ✏️ UPDATE PROMOTION DISCOUNT
# ==============================================

async def update_promotion_discount(
    *,
    promotion_id: int,
    discount_percent: float,
) -> None:

    await execute(
        """
        UPDATE promotions
        SET discount_percent = %s
        WHERE id = %s
        """,
        discount_percent,
        promotion_id,
    )

    logger.info(
        "promotion_discount_updated",
        extra={"promotion_id": promotion_id},
    )


# ==============================================
# ❌ DELETE PROMOTION
# ==============================================

async def delete_promotion(
    *,
    promotion_id: int,
) -> None:

    await execute(
        """
        DELETE FROM promotions
        WHERE id = %s
        """,
        promotion_id,
    )

    logger.info(
        "promotion_deleted",
        extra={"promotion_id": promotion_id},
    )
# ==============================================
# 💰 BRANCH PRICING REPOSITORY
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

BranchPricing = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_BRANCH_PRICING_SELECT = """
SELECT
    id,
    min_branches,
    max_branches,
    price_per_branch,
    active,
    created_at
FROM branch_pricing
"""

# ==============================================
# 🧩 ROW MAPPER
# ==============================================

def _row_to_branch_pricing(
    row,
) -> BranchPricing:

    return {
        "id": row["id"],
        "min_branches": row["min_branches"],
        "max_branches": row["max_branches"],
        "price_per_branch": float(row["price_per_branch"]),
        "active": row["active"],
        "created_at": row["created_at"],
    }


# ==============================================
# ➕ CREATE BRANCH PRICING
# ==============================================

async def create_branch_pricing(
    *,
    min_branches: int,
    max_branches: int | None,
    price_per_branch: float,
    active: bool = True,
) -> int:

    pricing_id = await insert_returning_id(
        """
        INSERT INTO branch_pricing
        (
            min_branches,
            max_branches,
            price_per_branch,
            active
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
        min_branches,
        max_branches,
        price_per_branch,
        active,
    )

    logger.info(
        "branch_pricing_created",
        extra={
            "pricing_id": pricing_id,
        },
    )

    return pricing_id


# ==============================================
# 🔍 GET BY ID
# ==============================================

async def get_branch_pricing_by_id(
    *,
    pricing_id: int,
) -> BranchPricing | None:

    row = await fetchrow(
        _BRANCH_PRICING_SELECT
        + """
        WHERE id = %s
        """,
        pricing_id,
    )

    if not row:
        return None

    return _row_to_branch_pricing(row)


# ==============================================
# 🔍 GET ACTIVE RULES
# ==============================================

async def get_active_branch_pricing() -> list[BranchPricing]:

    rows = await fetch(
        _BRANCH_PRICING_SELECT
        + """
        WHERE active = TRUE
        ORDER BY min_branches ASC
        """
    )

    return [
        _row_to_branch_pricing(row)
        for row in rows
    ]


# ==============================================
# 🔍 GET RULE FOR BRANCH COUNT
# ==============================================

async def get_branch_pricing_rule(
    *,
    branches_count: int,
) -> BranchPricing | None:

    row = await fetchrow(
        _BRANCH_PRICING_SELECT
        + """
        WHERE active = TRUE
        AND min_branches <= %s
        AND (
            max_branches IS NULL
            OR max_branches >= %s
        )
        ORDER BY min_branches DESC, id DESC
        LIMIT 1
        """,
        branches_count,
        branches_count,
    )

    if not row:
        return None

    return _row_to_branch_pricing(row)


# ==============================================
# 💰 CALCULATE BRANCH COST
# ==============================================

async def calculate_branch_cost(
    *,
    branches_count: int,
) -> float:

    if branches_count <= 1:
        return 0.0

    rule = await get_branch_pricing_rule(
        branches_count=branches_count,
    )

    if not rule:
        return 0.0

    extra_branches = branches_count - 1

    return (
        extra_branches
        * float(rule["price_per_branch"])
    )


# ==============================================
# ✏️ UPDATE PRICE
# ==============================================

async def update_branch_pricing_price(
    *,
    pricing_id: int,
    price_per_branch: float,
) -> None:

    await execute(
        """
        UPDATE branch_pricing
        SET price_per_branch = %s
        WHERE id = %s
        """,
        price_per_branch,
        pricing_id,
    )

    logger.info(
        "branch_pricing_price_updated",
        extra={
            "pricing_id": pricing_id,
            "price_per_branch": price_per_branch,
        },
    )


# ==============================================
# ✅ ACTIVATE RULE
# ==============================================

async def activate_branch_pricing(
    *,
    pricing_id: int,
) -> None:

    await execute(
        """
        UPDATE branch_pricing
        SET active = TRUE
        WHERE id = %s
        """,
        pricing_id,
    )

    logger.info(
        "branch_pricing_activated",
        extra={
            "pricing_id": pricing_id,
        },
    )


# ==============================================
# ❌ DEACTIVATE RULE
# ==============================================

async def deactivate_branch_pricing(
    *,
    pricing_id: int,
) -> None:

    await execute(
        """
        UPDATE branch_pricing
        SET active = FALSE
        WHERE id = %s
        """,
        pricing_id,
    )

    logger.info(
        "branch_pricing_deactivated",
        extra={
            "pricing_id": pricing_id,
        },
    )
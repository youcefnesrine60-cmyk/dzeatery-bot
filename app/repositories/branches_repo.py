# ==============================================
# 🏢 BRANCHES REPOSITORY
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

Branch = dict[str, object]

# ==============================================
# 📥 BASE SELECT
# ==============================================

BASE_SELECT = """
SELECT
    id,
    restaurant_id,
    name,
    phone,
    wilaya,
    lat,
    lng,
    is_active,
    created_at
FROM branches
"""

# ==============================================
# ➕ CREATE BRANCH
# ==============================================

async def create_branch(
    *,
    restaurant_id: int,
    name: str,
    phone: str | None = None,
    wilaya: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
) -> int:

    branch_id = await insert_returning_id(
        """
        INSERT INTO branches
        (
            restaurant_id,
            name,
            phone,
            wilaya,
            lat,
            lng
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
        restaurant_id,
        name,
        phone,
        wilaya,
        lat,
        lng,
    )

    logger.info(
        "branch_created",
        extra={
            "branch_id": branch_id,
            "restaurant_id": restaurant_id,
        },
    )

    return branch_id

# ==============================================
# 🔍 GET BRANCH
# ==============================================

async def get_branch(
    *,
    branch_id: int,
) -> Branch | None:

    row = await fetchrow(
        f"""
        {BASE_SELECT}
        WHERE id = %s
        """,
        branch_id,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# 🔍 GET RESTAURANT BRANCHES
# ==============================================

async def get_restaurant_branches(
    *,
    restaurant_id: int,
) -> list[Branch]:

    rows = await fetch(
        f"""
        {BASE_SELECT}
        WHERE restaurant_id = %s
        AND is_active = TRUE
        ORDER BY id
        """,
        restaurant_id,
    )

    return [dict(row) for row in rows]

# ==============================================
# 🔢 COUNT RESTAURANT BRANCHES
# ==============================================

async def count_restaurant_branches(
    *,
    restaurant_id: int,
) -> int:
    
    """
    حساب عدد فروع مطعم معين
    
    Args:
        restaurant_id: معرف المطعم
        
    Returns:
        int: عدد الفروع
    """

    row = await fetchrow(
        """
        SELECT COUNT(*) AS total
        FROM branches
        WHERE restaurant_id = %s
        AND is_active = TRUE
        """,
        restaurant_id,
    )

    if not row:
        return 0

    return int(row["total"])

# ==============================================
# ❌ DELETE BRANCH
# ==============================================

async def delete_branch(
    *,
    branch_id: int,
) -> None:

    await execute(
        """
        DELETE FROM branches
        WHERE id = %s
        """,
        branch_id,
    )

    logger.info(
        "branch_deleted",
        extra={
            "branch_id": branch_id,
        },
    )

# ==============================================
# ✏️ UPDATE BRANCH
# ==============================================

async def update_branch(
    *,
    branch_id: int,
    name: str,
    phone: str | None = None,
    wilaya: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
) -> None:

    await execute(
        """
        UPDATE branches
        SET
            name = %s,
            phone = %s,
            wilaya = %s,
            lat = %s,
            lng = %s
        WHERE id = %s
        """,
        name,
        phone,
        wilaya,
        lat,
        lng,
        branch_id,
    )

    logger.info(
        "branch_updated",
        extra={
            "branch_id": branch_id,
        },
    )

# ==============================================
# 🚫 DEACTIVATE BRANCH
# ==============================================

async def deactivate_branch(
    *,
    branch_id: int,
) -> None:

    await execute(
        """
        UPDATE branches
        SET is_active = FALSE
        WHERE id = %s
        """,
        branch_id,
    )

    logger.info(
        "branch_deactivated",
        extra={
            "branch_id": branch_id,
        },
    )

# ==============================================
# ✅ ACTIVATE BRANCH
# ==============================================

async def activate_branch(
    *,
    branch_id: int,
) -> None:

    await execute(
        """
        UPDATE branches
        SET is_active = TRUE
        WHERE id = %s
        """,
        branch_id,
    )

    logger.info(
        "branch_activated",
        extra={
            "branch_id": branch_id,
        },
    )
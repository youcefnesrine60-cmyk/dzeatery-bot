# ==============================================
# 📊 FEATURE USAGE LIMITS REPOSITORY
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

FeatureUsageLimit = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_FEATURE_USAGE_LIMIT_SELECT = """
SELECT
    id,
    plan_id,
    feature_id,
    monthly_limit,
    created_at,
    limit_type
FROM feature_usage_limits
"""


def _row_to_feature_usage_limit(row) -> FeatureUsageLimit:
    return {
        "id": row["id"],
        "plan_id": row["plan_id"],
        "feature_id": row["feature_id"],
        "monthly_limit": row["monthly_limit"],
        "created_at": row["created_at"],
        "limit_type": row["limit_type"],
    }


# ==============================================
# ➕ CREATE FEATURE USAGE LIMIT
# ==============================================

async def create_feature_usage_limit(
    *,
    plan_id: int,
    feature_id: int,
    monthly_limit: int | None,
    limit_type: str | None,
) -> int:

    limit_id = await insert_returning_id(
        """
        INSERT INTO feature_usage_limits (
            plan_id,
            feature_id,
            monthly_limit,
            limit_type
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        plan_id,
        feature_id,
        monthly_limit,
        limit_type,
    )

    logger.info(
        "feature_usage_limit_created",
        extra={
            "limit_id": limit_id,
            "plan_id": plan_id,
            "feature_id": feature_id,
        },
    )

    return limit_id


# ==============================================
# 🔍 GET LIMIT BY ID
# ==============================================

async def get_feature_usage_limit_by_id(
    *,
    limit_id: int,
) -> FeatureUsageLimit | None:

    row = await fetchrow(
        _FEATURE_USAGE_LIMIT_SELECT + """
        WHERE id = %s
        """,
        limit_id,
    )

    return _row_to_feature_usage_limit(row) if row else None


# ==============================================
# 🔍 GET PLAN FEATURE LIMIT
# ==============================================

async def get_plan_feature_limit(
    *,
    plan_id: int,
    feature_id: int,
) -> FeatureUsageLimit | None:

    row = await fetchrow(
        _FEATURE_USAGE_LIMIT_SELECT + """
        WHERE plan_id = %s
        AND feature_id = %s
        LIMIT 1
        """,
        plan_id,
        feature_id,
    )

    return _row_to_feature_usage_limit(row) if row else None


# ==============================================
# 🔍 GET PLAN LIMITS
# ==============================================

async def get_plan_feature_limits(
    *,
    plan_id: int,
) -> list[FeatureUsageLimit]:

    rows = await fetch(
        _FEATURE_USAGE_LIMIT_SELECT + """
        WHERE plan_id = %s
        ORDER BY id ASC
        """,
        plan_id,
    )

    return [
        _row_to_feature_usage_limit(row)
        for row in rows
    ]


# ==============================================
# 🔍 GET FEATURE LIMITS
# ==============================================

async def get_feature_limits(
    *,
    feature_id: int,
) -> list[FeatureUsageLimit]:

    rows = await fetch(
        _FEATURE_USAGE_LIMIT_SELECT + """
        WHERE feature_id = %s
        ORDER BY id ASC
        """,
        feature_id,
    )

    return [
        _row_to_feature_usage_limit(row)
        for row in rows
    ]


# ==============================================
# 🔍 GET ALL LIMITS
# ==============================================

async def get_all_feature_usage_limits() -> list[FeatureUsageLimit]:

    rows = await fetch(
        _FEATURE_USAGE_LIMIT_SELECT + """
        ORDER BY id ASC
        """
    )

    return [
        _row_to_feature_usage_limit(row)
        for row in rows
    ]


# ==============================================
# ✏️ UPDATE LIMIT
# ==============================================

async def update_feature_usage_limit(
    *,
    limit_id: int,
    monthly_limit: int | None,
    limit_type: str | None,
) -> None:

    await execute(
        """
        UPDATE feature_usage_limits
        SET
            monthly_limit = %s,
            limit_type = %s
        WHERE id = %s
        """,
        monthly_limit,
        limit_type,
        limit_id,
    )

    logger.info(
        "feature_usage_limit_updated",
        extra={
            "limit_id": limit_id,
        },
    )


# ==============================================
# ❌ DELETE LIMIT
# ==============================================

async def delete_feature_usage_limit(
    *,
    limit_id: int,
) -> None:

    await execute(
        """
        DELETE FROM feature_usage_limits
        WHERE id = %s
        """,
        limit_id,
    )

    logger.info(
        "feature_usage_limit_deleted",
        extra={
            "limit_id": limit_id,
        },
    )
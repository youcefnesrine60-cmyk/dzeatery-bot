# ==============================================
# 📦 PLAN FEATURES REPOSITORY
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

PlanFeature = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_PLAN_FEATURE_SELECT = """
SELECT
    pf.id,
    pf.plan_id,
    sp.code AS plan_code,
    sp.name AS plan_name,
    pf.feature_id,
    f.code AS feature_code,
    f.name AS feature_name,
    pf.included,
    pf.created_at
FROM plan_features pf
JOIN subscription_plans sp ON sp.id = pf.plan_id
JOIN features f ON f.id = pf.feature_id
"""

# ==============================================
# ➕ ADD FEATURE TO PLAN
# ==============================================

async def add_feature_to_plan(
    *,
    plan_id: int,
    feature_id: int,
    included: bool = True,
) -> int:

    plan_feature_id = await insert_returning_id(
        """
        INSERT INTO plan_features (
            plan_id,
            feature_id,
            included
        )
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        plan_id,
        feature_id,
        included,
    )

    logger.info(
        "feature_added_to_plan",
        extra={
            "plan_feature_id": plan_feature_id,
            "plan_id": plan_id,
            "feature_id": feature_id,
        },
    )

    return plan_feature_id


# ==============================================
# 🔍 GET PLAN FEATURE BY ID
# ==============================================

async def get_plan_feature_by_id(
    *,
    plan_feature_id: int,
) -> PlanFeature | None:

    row = await fetchrow(
        _PLAN_FEATURE_SELECT + " WHERE pf.id = %s",
        plan_feature_id,
    )

    return dict(row) if row else None


# ==============================================
# 🔍 GET PLAN FEATURES
# ==============================================

async def get_plan_features(
    *,
    plan_id: int,
) -> list[PlanFeature]:

    rows = await fetch(
        _PLAN_FEATURE_SELECT + """
        WHERE pf.plan_id = %s
        ORDER BY f.name ASC
        """,
        plan_id,
    )

    return [dict(row) for row in rows]


# ==============================================
# 🔍 GET INCLUDED FEATURES
# ==============================================

async def get_included_features(
    *,
    plan_id: int,
) -> list[PlanFeature]:

    rows = await fetch(
        _PLAN_FEATURE_SELECT + """
        WHERE pf.plan_id = %s
        AND pf.included = TRUE
        ORDER BY f.name ASC
        """,
        plan_id,
    )

    return [dict(row) for row in rows]


# ==============================================
# 🔍 HAS FEATURE
# ==============================================

async def plan_has_feature(
    *,
    plan_id: int,
    feature_id: int,
) -> bool:

    row = await fetchrow(
        """
        SELECT 1
        FROM plan_features
        WHERE plan_id = %s
          AND feature_id = %s
          AND included = TRUE
        LIMIT 1
        """,
        plan_id,
        feature_id,
    )

    return row is not None


# ==============================================
# ❌ REMOVE FEATURE FROM PLAN
# ==============================================

async def remove_feature_from_plan(
    *,
    plan_id: int,
    feature_id: int,
) -> None:

    await execute(
        """
        DELETE FROM plan_features
        WHERE plan_id = %s
          AND feature_id = %s
        """,
        plan_id,
        feature_id,
    )

    logger.info(
        "feature_removed_from_plan",
        extra={
            "plan_id": plan_id,
            "feature_id": feature_id,
        },
    )


# ==============================================
# ✏️ UPDATE INCLUDED FLAG
# ==============================================

async def update_feature_included_status(
    *,
    plan_id: int,
    feature_id: int,
    included: bool,
) -> None:

    await execute(
        """
        UPDATE plan_features
        SET included = %s
        WHERE plan_id = %s
          AND feature_id = %s
        """,
        included,
        plan_id,
        feature_id,
    )

    logger.info(
        "plan_feature_updated",
        extra={
            "plan_id": plan_id,
            "feature_id": feature_id,
            "included": included,
        },
    )
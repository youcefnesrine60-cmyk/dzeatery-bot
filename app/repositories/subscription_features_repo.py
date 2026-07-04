# ==============================================
# 🔗 SUBSCRIPTION FEATURES REPOSITORY
# Async Psycopg3 Version
# ==============================================

from psycopg import AsyncConnection

from app.core.logger import logger

from app.core.db import (
    execute, 
    fetch, 
    fetchrow, 
    insert_returning_id
)

# ==============================================
# 🧩 TYPES
# ==============================================

SubscriptionFeature = dict[str, object]

# ==============================================
# 🧩 BASE SELECT
# ==============================================

_SUBSCRIPTION_FEATURE_SELECT = """
SELECT
    sf.id,
    sf.subscription_id,
    sf.feature_id,
    f.code,
    f.name,
    f.description
FROM subscription_features sf
JOIN features f
    ON f.id = sf.feature_id
"""

# ==============================================
# ➕ CREATE SUBSCRIPTION FEATURE
# ==============================================

async def create_subscription_feature(
    *,
    subscription_id: int,
    feature_id: int,
) -> int:

    feature_link_id = await insert_returning_id(
        """
        INSERT INTO subscription_features
        (
            subscription_id,
            feature_id
        )
        VALUES
        (
            %s,
            %s
        )
        RETURNING id
        """,
        subscription_id,
        feature_id,
    )

    logger.info(
        "subscription_feature_created",
        extra={
            "id": feature_link_id,
            "subscription_id": subscription_id,
            "feature_id": feature_id,
        },
    )

    return feature_link_id


# ==============================================
# 🔍 GET FEATURES BY SUBSCRIPTION
# ==============================================

async def get_subscription_features(
    *,
    subscription_id: int,
) -> list[SubscriptionFeature]:

    rows = await fetch(
        _SUBSCRIPTION_FEATURE_SELECT + """
        WHERE sf.subscription_id = %s
        """,
        subscription_id,
    )

    return [
        {
            "id": row["id"],
            "subscription_id": row["subscription_id"],
            "feature_id": row["feature_id"],
            "feature_code": row["code"],
            "feature_name": row["name"],
            "feature_description": row["description"],
        }
        for row in rows
    ]


# ==============================================
# ❌ DELETE FEATURE FROM SUBSCRIPTION
# ==============================================

async def delete_subscription_feature(
    *,
    subscription_id: int,
    feature_id: int,
) -> None:

    await execute(
        """
        DELETE FROM subscription_features
        WHERE subscription_id = %s
        AND feature_id = %s
        """,
        subscription_id,
        feature_id,
    )

    logger.info(
        "subscription_feature_deleted",
        extra={
            "subscription_id": subscription_id,
            "feature_id": feature_id,
        },
    )

# ==============================================
# 🔍 CHECK SUBSCRIPTION HAS FEATURE
# ==============================================

async def subscription_has_feature(
    *,
    subscription_id: int,
    feature_id: int,
) -> bool:

    row = await fetchrow(
        """
        SELECT 1
        FROM subscription_features
        WHERE subscription_id = %s
          AND feature_id = %s
        LIMIT 1
        """,
        subscription_id,
        feature_id,
    )

    return row is not None

# ==============================================
# ➕ CREATE SUBSCRIPTION FEATURE (TX)
# ==============================================

async def create_subscription_feature_tx(
    *,
    conn: AsyncConnection,
    subscription_id: int,
    feature_id: int,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            INSERT INTO subscription_features
            (
                subscription_id,
                feature_id
            )
            VALUES
            (
                %s,
                %s
            )
            ON CONFLICT DO NOTHING
            """,
            (
                subscription_id,
                feature_id,
            ),
        )
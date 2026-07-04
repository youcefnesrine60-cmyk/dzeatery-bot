# ==============================================
# 🧾 SUBSCRIPTION FEATURE REQUESTS REPOSITORY
# Async Psycopg3 Version
# ==============================================
from psycopg.rows import dict_row
from psycopg import AsyncConnection

from app.core.logger import logger

from app.core.db import (
    execute,
    fetch,
    insert_returning_id,
)

# ==============================================
# 🧩 TYPES
# ==============================================

SubscriptionFeatureRequest = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

BASE_SELECT = """
SELECT
    id,
    subscription_id,
    feature_id,
    created_at
FROM subscription_feature_requests
"""

# ==============================================
# 🧩 ROW MAPPER
# ==============================================

def _row_to_request(
    row,
) -> SubscriptionFeatureRequest:

    return {
        "id": row["id"],
        "subscription_id": row["subscription_id"],
        "feature_id": row["feature_id"],
        "created_at": row["created_at"],
    }

# ==============================================
# ➕ CREATE REQUEST
# ==============================================

async def create_feature_request(
    *,
    subscription_id: int,
    feature_id: int,
) -> int:

    request_id = await insert_returning_id(
        """
        INSERT INTO subscription_feature_requests
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
        "subscription_feature_request_created",
        extra={
            "request_id": request_id,
            "subscription_id": subscription_id,
            "feature_id": feature_id,
        },
    )

    return request_id

# ==============================================
# 🔍 GET SUBSCRIPTION REQUESTS
# ==============================================

async def get_subscription_feature_requests(
    *,
    subscription_id: int,
) -> list[SubscriptionFeatureRequest]:

    rows = await fetch(
        BASE_SELECT + """
        WHERE subscription_id = %s
        ORDER BY id ASC
        """,
        subscription_id,
    )

    return [
        _row_to_request(row)
        for row in rows
    ]

# ==============================================
# ❌ DELETE SUBSCRIPTION REQUESTS
# حذف السجلات المؤقتة
# ==============================================

async def delete_subscription_feature_requests(
    *,
    subscription_id: int,
) -> None:

    await execute(
        """
        DELETE FROM subscription_feature_requests
        WHERE subscription_id = %s
        """,
        subscription_id,
    )

    logger.info(
        "subscription_feature_requests_deleted",
        extra={
            "subscription_id": subscription_id,
        },
    )

# ==============================================
# ❌ DELETE REQUESTS (TX)
# ==============================================

async def delete_subscription_feature_requests_tx(
    *,
    conn: AsyncConnection,
    subscription_id: int,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            DELETE FROM subscription_feature_requests
            WHERE subscription_id = %s
            """,
            (
                subscription_id,
            ),
        )

# ==============================================
# 🔍 GET REQUESTS (TX)
# ==============================================

async def get_subscription_feature_requests_tx(
    *,
    conn: AsyncConnection,
    subscription_id: int,
) -> list[SubscriptionFeatureRequest]:

    async with conn.cursor(row_factory=dict_row) as cur:

        await cur.execute(
            """
            SELECT
                id,
                subscription_id,
                feature_id,
                created_at
            FROM subscription_feature_requests
            WHERE subscription_id = %s
            ORDER BY id ASC
            """,
            (
                subscription_id,
            ),
        )

        rows = await cur.fetchall()

    return [
        _row_to_request(row)
        for row in rows
    ]
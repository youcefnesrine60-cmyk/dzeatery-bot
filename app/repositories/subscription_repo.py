# ==============================================
# 💳 SUBSCRIPTION REPOSITORY
# اشتراكات المطاعم
# إنشاء الاشتراك
# تفعيله
# إلغاؤه
# انتهاءه
# قراءة الاشتراكات
# Async Psycopg3 Version
# ==============================================

from datetime import datetime
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

Subscription = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_SUBSCRIPTION_SELECT = """
SELECT
    s.id,
    s.owner_id,
    s.restaurant_id,
    s.plan_id,
    sp.code AS plan_code,
    sp.name AS plan_name,
    sp.base_price,
    sp.plan_discount_percent,
    s.billing_cycle,
    s.amount,
    s.starts_at,
    s.expires_at,
    s.status,
    s.created_at
FROM subscriptions s
JOIN subscription_plans sp ON sp.id = s.plan_id
"""


def _row_to_subscription(row) -> Subscription:
    return {
        "id": row["id"],
        "owner_id": row["owner_id"],
        "restaurant_id": row["restaurant_id"],
        "plan_id": row["plan_id"],
        "plan_code": row["plan_code"],
        "plan_name": row["plan_name"],
        "base_price": row["base_price"],
        "plan_discount_percent": row["plan_discount_percent"],
        "billing_cycle": row["billing_cycle"],
        "amount": row["amount"],
        "starts_at": row["starts_at"],
        "expires_at": row["expires_at"],
        "status": row["status"],
        "created_at": row["created_at"],
    }


# ==============================================
# ➕ CREATE SUBSCRIPTION
# ==============================================

async def create_subscription(
    *,
    owner_id: int,
    restaurant_id: int,
    plan_id: int,
    billing_cycle: str,
    amount: float,
    starts_at: datetime | None,
    expires_at: datetime | None,
    status: str,
) -> int:

    subscription_id = await insert_returning_id(
        """
        INSERT INTO subscriptions (
            owner_id,
            restaurant_id,
            plan_id,
            billing_cycle,
            amount,
            starts_at,
            expires_at,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        owner_id,
        restaurant_id,
        plan_id,
        billing_cycle,
        amount,
        starts_at,
        expires_at,
        status,
    )

    logger.info(
        "subscription_created",
        extra={
            "subscription_id": subscription_id,
            "owner_id": owner_id,
            "restaurant_id": restaurant_id,
            "plan_id": plan_id,
        },
    )

    return subscription_id


# ==============================================
# 🔍 GET SUBSCRIPTION BY ID
# ==============================================

async def get_subscription_by_id(
    *,
    subscription_id: int,
) -> Subscription | None:

    row = await fetchrow(
        _SUBSCRIPTION_SELECT + " WHERE s.id = %s",
        subscription_id,
    )

    if not row:
        logger.warning(
            "subscription_not_found",
            extra={"subscription_id": subscription_id},
        )
        return None

    return _row_to_subscription(row)


# ==============================================
# 🔍 GET RESTAURANT SUBSCRIPTION
# ==============================================

async def get_restaurant_subscription(
    *,
    restaurant_id: int,
) -> Subscription | None:

    row = await fetchrow(
        _SUBSCRIPTION_SELECT + """
        WHERE s.restaurant_id = %s
          AND s.status IN ('active', 'trial')
          AND (
              s.expires_at IS NULL
              OR s.expires_at >= NOW()
          )
        ORDER BY s.id DESC
        LIMIT 1
        """,
        restaurant_id,
    )

    return _row_to_subscription(row) if row else None


# ==============================================
# 🔍 HAS ACTIVE SUBSCRIPTION
# ==============================================

async def has_active_subscription(
    *,
    restaurant_id: int,
) -> bool:

    row = await fetchrow(
        """
        SELECT 1
        FROM subscriptions
        WHERE restaurant_id = %s
          AND status IN ('active', 'trial')
          AND (
              expires_at IS NULL
              OR expires_at >= NOW()
          )
        LIMIT 1
        """,
        restaurant_id,
    )

    exists = row is not None

    logger.info(
        "active_subscription_checked",
        extra={
            "restaurant_id": restaurant_id,
            "exists": exists,
        },
    )

    return exists


# ==============================================
# 🔍 GET ACTIVE SUBSCRIPTION
# ==============================================

async def get_active_subscription(
    *,
    restaurant_id: int,
) -> Subscription | None:

    row = await fetchrow(
        _SUBSCRIPTION_SELECT + """
        WHERE s.restaurant_id = %s
          AND s.status IN ('active', 'trial')
          AND (
              s.expires_at IS NULL
              OR s.expires_at >= NOW()
          )
        ORDER BY s.id DESC
        LIMIT 1
        """,
        restaurant_id,
    )

    return _row_to_subscription(row) if row else None


# ==============================================
# 🔍 GET OWNER SUBSCRIPTIONS
# ==============================================

async def get_owner_subscriptions(
    *,
    owner_id: int,
) -> list[Subscription]:

    rows = await fetch(
        _SUBSCRIPTION_SELECT + """
        WHERE s.owner_id = %s
        ORDER BY s.id DESC
        """,
        owner_id,
    )

    subscriptions = [_row_to_subscription(row) for row in rows]

    logger.info(
        "owner_subscriptions_fetched",
        extra={
            "owner_id": owner_id,
            "count": len(subscriptions),
        },
    )

    return subscriptions


# ==============================================
# ✅ ACTIVATE SUBSCRIPTION
# ==============================================

async def activate_subscription(
    *,
    subscription_id: int,
    starts_at: datetime,
    expires_at: datetime,
) -> None:

    await execute(
        """
        UPDATE subscriptions
        SET
            status = 'active',
            starts_at = %s,
            expires_at = %s
        WHERE id = %s
        """,
        starts_at,
        expires_at,
        subscription_id,
    )

    logger.info(
        "subscription_activated",
        extra={"subscription_id": subscription_id},
    )


# ==============================================
# ❌ CANCEL SUBSCRIPTION
# ==============================================

async def cancel_subscription(
    *,
    subscription_id: int,
) -> None:

    await execute(
        """
        UPDATE subscriptions
        SET status = 'cancelled'
        WHERE id = %s
        """,
        subscription_id,
    )

    logger.info(
        "subscription_cancelled",
        extra={"subscription_id": subscription_id},
    )


# ==============================================
# ⌛ EXPIRE SUBSCRIPTION
# ==============================================

async def expire_subscription(
    *,
    subscription_id: int,
) -> None:

    await execute(
        """
        UPDATE subscriptions
        SET status = 'expired'
        WHERE id = %s
        """,
        subscription_id,
    )

    logger.info(
        "subscription_expired",
        extra={"subscription_id": subscription_id},
    )


# ==============================================
# 🔍 GET EXPIRING SUBSCRIPTIONS
# ==============================================

async def get_expiring_subscriptions() -> list[Subscription]:

    rows = await fetch(
        _SUBSCRIPTION_SELECT + """
        WHERE s.status = 'active'
          AND s.expires_at IS NOT NULL
          AND s.expires_at <= NOW() + INTERVAL '7 days'
          AND s.expires_at >= NOW()
        """
    )

    return [_row_to_subscription(row) for row in rows]

# ==============================================
# ✅ ACTIVATE SUBSCRIPTION (TX)
# ==============================================

async def activate_subscription_tx(
    *,
    conn: AsyncConnection,
    subscription_id: int,
    starts_at: datetime,
    expires_at: datetime,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            UPDATE subscriptions
            SET
                status = 'active',
                starts_at = %s,
                expires_at = %s
            WHERE id = %s
            AND status = 'pending'
            """,
            (
                starts_at,
                expires_at,
                subscription_id,
            ),
        )

        return cur.rowcount
# ==============================================
# 💳 SUBSCRIPTION PLAN REPOSITORY
# قراءة الباقات (Basic, Professional, Enterprise, Trial)
# قراءة السعر الأساسي
# قراءة نسبة التخفيض
# قراءة الكود
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

SubscriptionPlan = dict[str, object]

# ==============================================
# 🧩 BASE SELECT
# ==============================================

_PLAN_SELECT = """
SELECT
    id,
    code,
    name,
    active,
    created_at,
    plan_discount_percent,
    display_order,
    description,
    base_price
FROM subscription_plans
"""


def _row_to_plan(row) -> SubscriptionPlan:
    return {
        "id": row["id"],
        "code": row["code"],
        "name": row["name"],
        "active": row["active"],
        "created_at": row["created_at"],
        "plan_discount_percent": float(row["plan_discount_percent"]),
        "display_order": row["display_order"],
        "description": row["description"],
        "base_price": float(row["base_price"]),
    }


# ==============================================
# ➕ CREATE SUBSCRIPTION PLAN
# ==============================================

async def create_subscription_plan(
    *,
    code: str,
    name: str,
    base_price: float,
    plan_discount_percent: float = 0,
    display_order: int = 0,
    description: str | None = None,
    active: bool = True,
) -> int:

    plan_id = await insert_returning_id(
        """
        INSERT INTO subscription_plans (
            code,
            name,
            active,
            plan_discount_percent,
            display_order,
            description,
            base_price
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        code,
        name,
        active,
        plan_discount_percent,
        display_order,
        description,
        base_price,
    )

    logger.info(
        "subscription_plan_created",
        extra={
            "plan_id": plan_id,
            "code": code,
        },
    )

    return plan_id


# ==============================================
# 🔍 GET PLAN BY ID
# ==============================================

async def get_subscription_plan_by_id(
    *,
    plan_id: int,
) -> SubscriptionPlan | None:

    row = await fetchrow(
        _PLAN_SELECT + " WHERE id = %s",
        plan_id,
    )

    if not row:
        logger.warning(
            "subscription_plan_not_found",
            extra={"plan_id": plan_id},
        )
        return None

    return _row_to_plan(row)


# ==============================================
# 🔍 GET PLAN BY CODE
# ==============================================

async def get_subscription_plan_by_code(
    *,
    code: str,
) -> SubscriptionPlan | None:

    row = await fetchrow(
        _PLAN_SELECT + """
        WHERE code = %s
        LIMIT 1
        """,
        code,
    )

    return _row_to_plan(row) if row else None


# ==============================================
# 🎁 GET TRIAL PLAN
# ==============================================

async def get_trial_plan() -> SubscriptionPlan | None:

    return await get_subscription_plan_by_code(code="trial")


# ==============================================
# 🔍 GET ACTIVE PLANS
# ==============================================

async def get_active_subscription_plans() -> list[SubscriptionPlan]:

    rows = await fetch(
        _PLAN_SELECT + """
        WHERE active = TRUE
        ORDER BY display_order ASC, id ASC
        """
    )

    plans = [_row_to_plan(row) for row in rows]

    logger.info(
        "subscription_plans_fetched",
        extra={"count": len(plans)},
    )

    return plans


# ==============================================
# 🔍 GET ALL PLANS
# ==============================================

async def get_all_subscription_plans() -> list[SubscriptionPlan]:

    rows = await fetch(
        _PLAN_SELECT + """
        ORDER BY display_order ASC, id ASC
        """
    )

    return [_row_to_plan(row) for row in rows]


# ==============================================
# 💰 CALCULATE PLAN PRICE
# ==============================================

async def calculate_plan_price(
    *,
    plan_id: int,
) -> float:

    plan = await get_subscription_plan_by_id(plan_id=plan_id)

    if not plan:
        raise ValueError("subscription_plan_not_found")

    base_price = float(plan["base_price"])
    discount = float(plan["plan_discount_percent"])

    final_price = base_price - (base_price * discount / 100)

    return round(final_price, 2)


# ==============================================
# ✏️ UPDATE PLAN PRICE
# ==============================================

async def update_subscription_plan_price(
    *,
    plan_id: int,
    base_price: float,
) -> None:

    await execute(
        """
        UPDATE subscription_plans
        SET base_price = %s
        WHERE id = %s
        """,
        base_price,
        plan_id,
    )

    logger.info(
        "subscription_plan_price_updated",
        extra={
            "plan_id": plan_id,
            "base_price": base_price,
        },
    )


# ==============================================
# ✏️ UPDATE PLAN DISCOUNT
# ==============================================

async def update_subscription_plan_discount(
    *,
    plan_id: int,
    plan_discount_percent: float,
) -> None:

    await execute(
        """
        UPDATE subscription_plans
        SET plan_discount_percent = %s
        WHERE id = %s
        """,
        plan_discount_percent,
        plan_id,
    )

    logger.info(
        "subscription_plan_discount_updated",
        extra={
            "plan_id": plan_id,
            "plan_discount_percent": plan_discount_percent,
        },
    )


# ==============================================
# ✅ ACTIVATE PLAN
# ==============================================

async def activate_subscription_plan(
    *,
    plan_id: int,
) -> None:

    await execute(
        """
        UPDATE subscription_plans
        SET active = TRUE
        WHERE id = %s
        """,
        plan_id,
    )

    logger.info(
        "subscription_plan_activated",
        extra={"plan_id": plan_id},
    )


# ==============================================
# ❌ DEACTIVATE PLAN
# ==============================================

async def deactivate_subscription_plan(
    *,
    plan_id: int,
) -> None:

    await execute(
        """
        UPDATE subscription_plans
        SET active = FALSE
        WHERE id = %s
        """,
        plan_id,
    )

    logger.info(
        "subscription_plan_deactivated",
        extra={"plan_id": plan_id},
    )
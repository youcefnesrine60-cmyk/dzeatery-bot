# ==============================================
# 📊 FEATURE USAGE COUNTER ENGINE
# Business Logic Layer
# ✓ إنشاء العداد تلقائياً إذا لم يوجد
# ✓ قراءة الاستخدام الحالي
# ✓ زيادة الاستخدام
# ✓ إنقاص الاستخدام
# ✓ التحقق من limit قبل الزيادة
# ✓ التكامل مع feature_guard.py
# ==============================================

from datetime import datetime, timezone
from psycopg import AsyncConnection

from app.core.logger import logger

from app.repositories.feature_usage_limits_repo import get_plan_feature_limit
from app.repositories.feature_usage_counter_repo import (
    get_feature_counter,
    create_feature_counter,
    increment_feature_counter,
    decrement_feature_counter,
    get_current_usage,
)

from app.repositories.feature_usage_counter_repo import (
    get_feature_counter_tx,
    create_feature_counter_tx,
    increment_feature_counter_tx,
)


# ==============================================
# 🔍 CURRENT PERIOD
# ==============================================

def _current_period() -> tuple[int, int]:

    now = datetime.now(timezone.utc)

    return (
        now.year,
        now.month,
    )

# ==============================================
# 🔍 GET CURRENT USAGE
# ==============================================

async def get_usage(
    *,
    restaurant_id: int,
    feature_id: int,
) -> int:

    year, month = _current_period()

    return await get_current_usage(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
        period_year=year,
        period_month=month,
    )

# ==============================================
# 🔍 CAN USE FEATURE
# ==============================================

async def can_use_feature(
    *,
    restaurant_id: int,
    plan_id: int,
    feature_id: int,
    amount: int = 1,
) -> bool:

    limit_row = await get_plan_feature_limit(
        plan_id=plan_id,
        feature_id=feature_id,
    )

    if not limit_row:
        return True

    monthly_limit = limit_row["monthly_limit"]

    if monthly_limit is None:
        return True

    current_usage = await get_usage(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
    )

    return (current_usage + amount) <= monthly_limit

# ==============================================
# ➕ INCREASE USAGE
# ==============================================

async def increase_usage(
    *,
    restaurant_id: int,
    feature_id: int,
    amount: int = 1,
) -> int:

    year, month = _current_period()

    counter = await get_feature_counter(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
        period_year=year,
        period_month=month,
    )

    if not counter:

        counter_id = await create_feature_counter(
            restaurant_id=restaurant_id,
            feature_id=feature_id,
            usage_count=0,
            period_year=year,
            period_month=month,
        )

    else:

        counter_id = counter["id"]

    await increment_feature_counter(
        counter_id=counter_id,
        amount=amount,
    )

    usage = await get_usage(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
    )

    logger.info(
        "feature_usage_increased",
        extra={
            "restaurant_id": restaurant_id,
            "feature_id": feature_id,
            "usage": usage,
        },
    )

    return usage

# ==============================================
# ➖ DECREASE USAGE
# ==============================================

async def decrease_usage(
    *,
    restaurant_id: int,
    feature_id: int,
    amount: int = 1,
) -> int:

    year, month = _current_period()

    counter = await get_feature_counter(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
        period_year=year,
        period_month=month,
    )

    if not counter:
        return 0

    await decrement_feature_counter(
        counter_id=counter["id"],
        amount=amount,
    )

    usage = await get_usage(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
    )

    logger.info(
        "feature_usage_decreased",
        extra={
            "restaurant_id": restaurant_id,
            "feature_id": feature_id,
            "usage": usage,
        },
    )

    return usage

# ==============================================
# 🔍 GET REMAINING USAGE
# ==============================================

async def get_remaining_usage(
    *,
    restaurant_id: int,
    plan_id: int,
    feature_id: int,
) -> int | None:

    limit_row = await get_plan_feature_limit(
        plan_id=plan_id,
        feature_id=feature_id,
    )

    if not limit_row:
        return None

    monthly_limit = limit_row["monthly_limit"]

    if monthly_limit is None:
        return None

    usage = await get_usage(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
    )

    return max(
        monthly_limit - usage,
        0,
    )

# ==============================================
# ➕ INCREASE USAGE (TX)
# ==============================================

async def increase_usage_tx(
    *,
    conn: AsyncConnection,
    restaurant_id: int,
    feature_id: int,
    amount: int = 1,
) -> int:

    now = datetime.now(timezone.utc)

    period_year = now.year
    period_month = now.month

    counter = await get_feature_counter_tx(
        conn=conn,
        restaurant_id=restaurant_id,
        feature_id=feature_id,
        period_year=period_year,
        period_month=period_month,
    )

    if not counter:

        counter_id = await create_feature_counter_tx(
            conn=conn,
            restaurant_id=restaurant_id,
            feature_id=feature_id,
            usage_count=0,
            period_year=period_year,
            period_month=period_month,
        )

        current_usage = 0

    else:

        counter_id = counter["id"]
        current_usage = counter["usage_count"]

    await increment_feature_counter_tx(
        conn=conn,
        counter_id=counter_id,
        amount=amount,
    )

    new_usage = current_usage + amount

    logger.info(
        "feature_usage_increased_tx",
        extra={
            "restaurant_id": restaurant_id,
            "feature_id": feature_id,
            "usage": new_usage,
        },
    )

    return new_usage
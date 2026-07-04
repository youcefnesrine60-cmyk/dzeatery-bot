# ==============================================
# 📊 FEATURE USAGE LIMITS ENGINE
# Business Layer
# ==============================================

from app.core.logger import logger
from app.guards.subscription_guard import require_active_subscription
from app.repositories.feature_usage_limits_repo import get_plan_feature_limit

# ==============================================
# 🔍 GET FEATURE LIMIT
# ==============================================

async def get_feature_limit(
    *,
    restaurant_id: int,
    feature_id: int,
) -> int | None:

    subscription = await require_active_subscription(
        restaurant_id=restaurant_id,
    )

    limit_row = await get_plan_feature_limit(
        plan_id=subscription["plan_id"],
        feature_id=feature_id,
    )

    if not limit_row:
        return None

    if limit_row["monthly_limit"] is None:
        return None

    return int(limit_row["monthly_limit"])


# ==============================================
# 🔍 HAS AVAILABLE USAGE
# ==============================================

async def has_available_usage(
    *,
    restaurant_id: int,
    feature_id: int,
    current_usage: int,
) -> bool:

    limit_value = await get_feature_limit(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
    )

    # Unlimited
    if limit_value is None:
        return True

    return current_usage < limit_value


# ==============================================
# 🚫 REQUIRE AVAILABLE USAGE
# ==============================================

async def require_available_usage(
    *,
    restaurant_id: int,
    feature_id: int,
    current_usage: int,
) -> None:

    allowed = await has_available_usage(
        restaurant_id=restaurant_id,
        feature_id=feature_id,
        current_usage=current_usage,
    )

    if allowed:
        return

    logger.warning(
        "feature_usage_limit_exceeded",
        extra={
            "restaurant_id": restaurant_id,
            "feature_id": feature_id,
            "current_usage": current_usage,
        },
    )

    raise ValueError(
        "feature_usage_limit_exceeded"
    )
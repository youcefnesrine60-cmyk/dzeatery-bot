# ==============================================
# 🔐 FEATURE GUARD
# Subscription + Limits Protection Layer
# ==============================================

from app.core.logger import logger

from app.guards.subscription_guard import (
    get_valid_subscription,
)

from app.repositories.subscription_features_repo import (
    subscription_has_feature,
)

from app.services.business.feature_usage_counter_engine import (
    can_use_feature,
)

# ==============================================
# 🧩 TYPES
# ==============================================

Subscription = dict[str, object]

# ==============================================
# 🔍 CHECK FEATURE ACCESS
# ==============================================

async def check_feature_access(
    *,
    restaurant_id: int,
    feature_id: int,
) -> bool:

    try:

        await require_feature(
            restaurant_id=restaurant_id,
            feature_id=feature_id,
        )

        return True

    except ValueError:

        return False

# ==============================================
# 🚫 REQUIRE FEATURE
# ==============================================

async def require_feature(
    *,
    restaurant_id: int,
    feature_id: int,
) -> Subscription:

    # ------------------------------------------
    # 1️⃣ GET ACTIVE SUBSCRIPTION
    # ------------------------------------------

    subscription = await get_valid_subscription(
        restaurant_id=restaurant_id,
    )

    if not subscription:
        logger.warning(
            "no_active_subscription",
            extra={
                "restaurant_id": restaurant_id,
            },
        )
        raise ValueError("no_active_subscription")

    # ------------------------------------------
    # 2️⃣ CHECK PLAN FEATURE ACCESS
    # ------------------------------------------

    has_feature = await subscription_has_feature(
        subscription_id=subscription["id"],
        feature_id=feature_id,
    )

    if not has_feature:

        logger.warning(
            "feature_not_available",
            extra={
                "restaurant_id": restaurant_id,
                "subscription_id": subscription["id"],
                "feature_id": feature_id,
            },
        )

        raise ValueError("feature_not_available")

    # ------------------------------------------
    # 3️⃣ CHECK USAGE LIMITS
    # ------------------------------------------

    allowed = await can_use_feature(
        restaurant_id=restaurant_id,
        plan_id=subscription["plan_id"],
        feature_id=feature_id,
        amount=1,
    )

    if not allowed:

        logger.warning(
            "feature_limit_reached",
            extra={
                "restaurant_id": restaurant_id,
                "subscription_id": subscription["id"],
                "feature_id": feature_id,
            },
        )

        raise ValueError("feature_limit_reached")

    # ------------------------------------------
    # SUCCESS
    # ------------------------------------------

    return subscription


# ==============================================
# 🔍 HAS FEATURE (SHORTCUT)
# ==============================================

async def has_feature(
    *,
    restaurant_id: int,
    feature_id: int,
) -> bool:

    try:
        await require_feature(
            restaurant_id=restaurant_id,
            feature_id=feature_id,
        )
        return True

    except ValueError:
        return False
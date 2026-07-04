# ==============================================
# 🛡️ SUBSCRIPTION GUARD
# التحقق من صلاحية الاشتراك
# منع الوصول عند انتهاء الاشتراك
# منع الوصول عند عدم وجود اشتراك
# ==============================================

from app.core.logger import logger

from app.repositories.subscription_repo import get_active_subscription

# ==============================================
# 🧩 TYPES
# ==============================================

Subscription = dict[str, object]

# ==============================================
# ✅ REQUIRE ACTIVE SUBSCRIPTION
# ==============================================

async def require_active_subscription(
    *,
    restaurant_id: int,
) -> Subscription:

    subscription = await get_active_subscription(
        restaurant_id=restaurant_id,
    )

    if not subscription:

        logger.warning(
            "active_subscription_required",
            extra={
                "restaurant_id": restaurant_id,
            },
        )

        raise ValueError(
            "active_subscription_required"
        )

    return subscription


# ==============================================
# 🔍 HAS ACTIVE SUBSCRIPTION
# ==============================================

async def has_active_subscription(
    *,
    restaurant_id: int,
) -> bool:

    subscription = await get_active_subscription(
        restaurant_id=restaurant_id,
    )

    return subscription is not None


# ==============================================
# 🔍 GET CURRENT SUBSCRIPTION
# ==============================================

async def get_current_subscription(
    *,
    restaurant_id: int,
) -> Subscription | None:

    return await get_active_subscription(
        restaurant_id=restaurant_id,
    )


# ==============================================
# 🔍 IS TRIAL SUBSCRIPTION
# ==============================================

async def is_trial_subscription(
    *,
    restaurant_id: int,
) -> bool:

    subscription = await get_active_subscription(
        restaurant_id=restaurant_id,
    )

    if not subscription:
        return False

    return subscription["status"] == "trial"


# ==============================================
# 🔍 IS PAID SUBSCRIPTION
# ==============================================

async def is_paid_subscription(
    *,
    restaurant_id: int,
) -> bool:

    subscription = await get_active_subscription(
        restaurant_id=restaurant_id,
    )

    if not subscription:
        return False

    return subscription["status"] == "active"


# ==============================================
# 🔍 GET PLAN CODE
# ==============================================

async def get_subscription_plan_code(
    *,
    restaurant_id: int,
) -> str | None:

    subscription = await get_active_subscription(
        restaurant_id=restaurant_id,
    )

    if not subscription:
        return None

    return subscription["plan_code"]

async def get_valid_subscription(
        *,
        restaurant_id: int
) -> Subscription:
    
    return await require_active_subscription(
        restaurant_id=restaurant_id
    )
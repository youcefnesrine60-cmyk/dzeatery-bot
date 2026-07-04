#==============================================
#       💳 SUBSCRIPTION SERVICE
#       Business Logic Layer
#       بناء طبقة الاشتراكات
#       لتجربة المجانية (trial)
#       الباقة الشهرية
#       الباقة السنوية (+ شهرين مجانيين)
#       حساب تاريخ الانتهاء
#     منع تكرار التجربة المجانية
#===============================================

from datetime import datetime, timedelta, timezone

from app.core.logger import logger

from app.repositories.owner_repo import (
    has_used_trial, 
    mark_trial_used
)
from app.repositories.subscription_repo import create_subscription
from app.repositories.subscription_plan_repo import get_subscription_plan_by_code
from app.repositories.subscription_feature_requests_repo import create_feature_request
from app.repositories.plan_features_repo import get_plan_features
from app.repositories.subscription_features_repo import create_subscription_feature
from app.repositories.payment_repo import create_payment

from app.services.business.pricing_service import calculate_subscription_pricing


# ==============================================
# CREATE TRIAL SUBSCRIPTION
# ==============================================

async def create_trial_subscription(
    *,
    owner_id: int,
    restaurant_id: int,
    payment_method: str = "cash",
) -> int:
    if await has_used_trial(owner_id=owner_id):
        raise ValueError("trial_already_used")

    trial_plan = await get_subscription_plan_by_code(code="trial")
    if not trial_plan:
        raise ValueError("trial_plan_not_found")

    starts_at = datetime.now(timezone.utc)
    expires_at = starts_at + timedelta(days=30)

    subscription_id = await create_subscription(
        owner_id=owner_id,
        restaurant_id=restaurant_id,
        plan_id=trial_plan["id"],
        billing_cycle="trial",
        amount=0,
        starts_at=starts_at,
        expires_at=expires_at,
        status="trial",
    )

    features = await get_plan_features(plan_id=trial_plan["id"])
    for feature in features:
        await create_subscription_feature(
            subscription_id=subscription_id,
            feature_id=feature["feature_id"],
        )

    await mark_trial_used(owner_id=owner_id)

    logger.info(
        "trial_subscription_created",
        extra={
            "subscription_id": subscription_id,
            "restaurant_id": restaurant_id,
        },
    )

    return subscription_id


# ==============================================
# CREATE PAID SUBSCRIPTION
# ==============================================

async def create_paid_subscription(
    *,
    owner_id: int,
    restaurant_id: int,
    plan_id: int,
    billing_cycle: str,
    payment_method: str,
    restaurants_count: int,
    branches_count: int,
    years_with_platform: int,
    products_count: int,
    categories_count: int,
    monthly_orders: int,
    average_order_value: float,
    additional_feature_ids: list[int] | None = None,
) -> dict[str, object]:
    pricing = await calculate_subscription_pricing(  # ✅ إضافة await
        plan_id=plan_id,
        billing_cycle=billing_cycle,
        payment_method=payment_method,
        restaurants_count=restaurants_count,
        branches_count=branches_count,
        years_with_platform=years_with_platform,
        products_count=products_count,
        categories_count=categories_count,
        monthly_orders=monthly_orders,
        average_order_value=average_order_value,
        additional_feature_ids=additional_feature_ids or [],
    )

    subscription_id = await create_subscription(
        owner_id=owner_id,
        restaurant_id=restaurant_id,
        plan_id=plan_id,
        billing_cycle=billing_cycle,
        amount=pricing["final_amount_due"],
        starts_at=None,
        expires_at=None,
        status="pending_payment",
    )

    payment_id = await create_payment(
        owner_id=owner_id,
        restaurant_id=restaurant_id,
        subscription_id=subscription_id,
        payment_method=payment_method,
        amount=pricing["final_amount_due"],
        status="pending",
    )

    features = await get_plan_features(plan_id=plan_id)
    for feature in features:
        await create_feature_request(
            subscription_id=subscription_id,
            feature_id=feature["feature_id"],
        )

    for feature_id in (additional_feature_ids or []):
        await create_feature_request(
            subscription_id=subscription_id,
            feature_id=feature_id,
        )

    logger.info(
        "paid_subscription_created",
        extra={
            "subscription_id": subscription_id,
            "payment_id": payment_id,
            "restaurant_id": restaurant_id,
            "amount": pricing["final_amount_due"],
        },
    )

    return {
        "subscription_id": subscription_id,
        "payment_id": payment_id,
        "pricing": pricing,
    }


# ==============================================
# CALCULATE SUBSCRIPTION ONLY (PREVIEW)
# ==============================================

async def preview_subscription_pricing(
    *,
    plan_id: int,
    billing_cycle: str,
    payment_method: str,
    restaurants_count: int,
    branches_count: int,
    years_with_platform: int,
    products_count: int,
    categories_count: int,
    monthly_orders: int,
    average_order_value: float,
    additional_feature_ids: list[int] | None = None,
) -> dict[str, object]:
    # ✅ إضافة await لأن calculate_subscription_pricing هي دالة غير متزامنة
    return await calculate_subscription_pricing(
        plan_id=plan_id,
        billing_cycle=billing_cycle,
        payment_method=payment_method,
        restaurants_count=restaurants_count,
        branches_count=branches_count,
        years_with_platform=years_with_platform,
        products_count=products_count,
        categories_count=categories_count,
        monthly_orders=monthly_orders,
        average_order_value=average_order_value,
        additional_feature_ids=additional_feature_ids or [],
    )
# ==============================================
# 📝 REGISTRATION SERVICE
# Business Logic Layer
#
# Registration Request
#        ↓
# Admin Approval
#        ↓
# Create Owner
#        ↓
# Create Restaurant
#        ↓
# Create Restaurant Metrics
#        ↓
# Create Trial Subscription
#        ↓
# Create Subscription Features
#        ↓
# Owner Approved
#        ↓
# Registration Request Approved
# ==============================================

from app.core.logger import logger

from app.repositories.registration_request_repo import (
    approve_registration_request,
    get_registration_request_by_id,
    reject_registration_request,
)
from app.services.business.owner_service import (
    approve_owner,
    get_or_create_owner,
)

from app.repositories.restaurant_repo import create_restaurant
from app.repositories.restaurant_metrics_repo import create_restaurant_metrics
from app.services.business.subscription_service import create_trial_subscription

# ==============================================
# 🧩 TYPES
# ==============================================

RegistrationResult = dict[str, int]

# ==============================================
# ✅ APPROVE REGISTRATION
# ==============================================

async def approve_registration(
    *,
    request_id: int,
) -> RegistrationResult:

    request = await get_registration_request_by_id(
        request_id=request_id,
    )

    if not request:
        raise ValueError(
            "registration_request_not_found"
        )

    owner_id = await get_or_create_owner(
        chat_id=request["chat_id"],
        full_name=request["full_name"],
        phone=request["owner_phone"],
        email=request["email"] or "",
    )

    restaurant_id = await create_restaurant(
        owner_id=owner_id,
        name=request["restaurant_name"],
        restaurant_type=request["restaurant_type"],
        phone=request["restaurant_phone"],
        wilaya=request["wilaya"],
        lat=request["lat"],
        lng=request["lng"],
    )

    await create_restaurant_metrics(
        restaurant_id=restaurant_id,
    )

    subscription_id = await create_trial_subscription(
        owner_id=owner_id,
        restaurant_id=restaurant_id,
    )

    await approve_owner(
        owner_id=owner_id,
    )

    await approve_registration_request(
        request_id=request_id,
    )

    logger.info(
        "registration_approved",
        extra={
            "request_id": request_id,
            "owner_id": owner_id,
            "restaurant_id": restaurant_id,
            "subscription_id": subscription_id,
        },
    )

    return {
        "owner_id": owner_id,
        "restaurant_id": restaurant_id,
        "subscription_id": subscription_id,
    }

# ==============================================
# ❌ REJECT REGISTRATION
# ==============================================

async def reject_registration(
    *,
    request_id: int,
) -> None:

    request = await get_registration_request_by_id(
        request_id=request_id,
    )

    if not request:
        raise ValueError(
            "registration_request_not_found"
        )

    await reject_registration_request(
        request_id=request_id,
    )

    logger.info(
        "registration_rejected",
        extra={
            "request_id": request_id,
            "chat_id": request["chat_id"],
        },
    )

# ==============================================
# 🔍 PREVIEW REGISTRATION REQUEST
# ==============================================

async def get_registration_preview(
    *,
    request_id: int,
) -> dict[str, object] | None:

    return await get_registration_request_by_id(
        request_id=request_id,
    )
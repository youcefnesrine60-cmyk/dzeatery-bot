# ==============================================
# 👤 OWNER SERVICE
# Business Logic Layer
# ==============================================

from app.core.logger import logger

from app.repositories.owner_repo import (
    create_owner,
    get_owner_by_chat_id,
    has_used_trial,
    mark_trial_used,
    update_registration_status,
)

# ==============================================
# 🧩 TYPES
# ==============================================

Owner = dict[str, object]

# ==============================================
# 👤 GET OR CREATE OWNER
# ==============================================

async def get_or_create_owner(
    *,
    chat_id: int,
    full_name: str,
    phone: str,
    email: str,
) -> int:

    owner = await get_owner_by_chat_id(
        chat_id=chat_id,
    )

    if owner:

        logger.info(
            "owner_already_exists",
            extra={
                "owner_id": owner["id"],
                "chat_id": chat_id,
            },
        )

        return int(owner["id"])

    owner_id = await create_owner(
        chat_id=chat_id,
        full_name=full_name,
        phone=phone,
        email=email,
    )

    logger.info(
        "owner_created_from_service",
        extra={
            "owner_id": owner_id,
            "chat_id": chat_id,
        },
    )

    return owner_id


# ==============================================
# 🎁 CAN USE TRIAL
# ==============================================

async def can_use_trial(
    *,
    owner_id: int,
) -> bool:

    return not await has_used_trial(
        owner_id=owner_id,
    )


# ==============================================
# 🎁 ACTIVATE TRIAL USAGE
# ==============================================

async def activate_trial_usage(
    *,
    owner_id: int,
) -> None:

    await mark_trial_used(
        owner_id=owner_id,
    )

    logger.info(
        "trial_usage_activated",
        extra={
            "owner_id": owner_id,
        },
    )


# ==============================================
# ✅ APPROVE OWNER
# ==============================================

async def approve_owner(
    *,
    owner_id: int,
) -> None:

    await update_registration_status(
        owner_id=owner_id,
        status="approved",
    )

    logger.info(
        "owner_approved",
        extra={
            "owner_id": owner_id,
        },
    )


# ==============================================
# ❌ REJECT OWNER
# ==============================================

async def reject_owner(
    *,
    owner_id: int,
) -> None:

    await update_registration_status(
        owner_id=owner_id,
        status="rejected",
    )

    logger.info(
        "owner_rejected",
        extra={
            "owner_id": owner_id,
        },
    )


# ==============================================
# ⏳ SET PENDING
# ==============================================

async def set_owner_pending(
    *,
    owner_id: int,
) -> None:

    await update_registration_status(
        owner_id=owner_id,
        status="pending",
    )

    logger.info(
        "owner_pending",
        extra={
            "owner_id": owner_id,
        },
    )
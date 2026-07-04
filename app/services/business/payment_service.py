# ==============================================
# 💳 PAYMENT SERVICE
# Business Logic Layer
# إنشاء عملية دفع جديدة.
# منع الدفع المكرر لنفس الاشتراك.
# تأكيد الدفع.
# فشل الدفع.
# إلغاء الدفع.
# قراءة حالة الدفع.
# تجهيز الطبقة التي سيستخدمها لاحقاً payment_callback.py.
# ==============================================

from datetime import datetime, UTC

from app.core.logger import logger

from app.repositories.payment_repo import (
    create_payment,
    get_payment_by_id,
    get_payment_by_reference,
    mark_payment_paid,
    mark_payment_failed,
    cancel_payment,
)

# ==============================================
# 🧩 TYPES
# ==============================================

Payment = dict[str, object]

# ==============================================
# ➕ CREATE PAYMENT REQUEST
# ==============================================

async def create_payment_request(
    *,
    owner_id: int,
    restaurant_id: int,
    subscription_id: int | None,
    payment_method: str,
    amount: float,
    external_reference: str | None = None,
) -> int:

    if amount <= 0:
        raise ValueError("invalid_payment_amount")

    payment_id = await create_payment(
        owner_id=owner_id,
        restaurant_id=restaurant_id,
        subscription_id=subscription_id,
        payment_method=payment_method,
        amount=amount,
        status="pending",
        external_reference=external_reference,
    )

    logger.info(
        "payment_request_created",
        extra={
            "payment_id": payment_id,
            "restaurant_id": restaurant_id,
            "amount": amount,
        },
    )

    return payment_id


# ==============================================
# 🔍 GET PAYMENT
# ==============================================

async def get_payment(
    *,
    payment_id: int,
) -> Payment | None:

    return await get_payment_by_id(
        payment_id=payment_id,
    )


# ==============================================
# 🔍 GET PAYMENT BY REFERENCE
# ==============================================

async def get_payment_by_external_reference(
    *,
    external_reference: str,
) -> Payment | None:

    return await get_payment_by_reference(
        external_reference=external_reference,
    )


# ==============================================
# ✅ CONFIRM PAYMENT
# ==============================================

async def confirm_payment(
    *,
    payment_id: int,
) -> None:

    payment = await get_payment_by_id(
        payment_id=payment_id,
    )

    if not payment:
        raise ValueError("payment_not_found")

    status = payment["status"]

    if status == "paid":

        logger.info(
            "payment_already_paid",
            extra={"payment_id": payment_id},
        )

        return

    if status == "failed":
        raise ValueError("cannot_confirm_failed_payment")

    if status == "cancelled":
        raise ValueError("cannot_confirm_cancelled_payment")

    await mark_payment_paid(
        payment_id=payment_id,
        paid_at=datetime.now(UTC),
    )

    logger.info(
        "payment_confirmed",
        extra={"payment_id": payment_id},
    )


# ==============================================
# ❌ FAIL PAYMENT
# ==============================================

async def fail_payment(
    *,
    payment_id: int,
) -> None:

    payment = await get_payment_by_id(
        payment_id=payment_id,
    )

    if not payment:
        raise ValueError("payment_not_found")

    status = payment["status"]

    if status == "paid":
        raise ValueError("cannot_fail_paid_payment")

    if status == "cancelled":
        raise ValueError("cannot_fail_cancelled_payment")

    if status == "failed":

        logger.info(
            "payment_already_failed",
            extra={"payment_id": payment_id},
        )

        return

    await mark_payment_failed(
        payment_id=payment_id,
    )

    logger.info(
        "payment_failed",
        extra={"payment_id": payment_id},
    )


# ==============================================
# 🚫 CANCEL PAYMENT
# ==============================================

async def cancel_payment_request(
    *,
    payment_id: int,
) -> None:

    payment = await get_payment_by_id(
        payment_id=payment_id,
    )

    if not payment:
        raise ValueError("payment_not_found")

    status = payment["status"]

    if status == "paid":
        raise ValueError("cannot_cancel_paid_payment")

    if status == "failed":
        raise ValueError("cannot_cancel_failed_payment")

    if status == "cancelled":

        logger.info(
            "payment_already_cancelled",
            extra={"payment_id": payment_id},
        )

        return

    await cancel_payment(
        payment_id=payment_id,
    )

    logger.info(
        "payment_cancelled_from_service",
        extra={"payment_id": payment_id},
    )


# ==============================================
# 🔍 IS PAYMENT PAID
# ==============================================

async def is_payment_paid(
    *,
    payment_id: int,
) -> bool:

    payment = await get_payment_by_id(
        payment_id=payment_id,
    )

    return bool(
        payment
        and payment["status"] == "paid"
    )


# ==============================================
# 🔍 IS PAYMENT PENDING
# ==============================================

async def is_payment_pending(
    *,
    payment_id: int,
) -> bool:

    payment = await get_payment_by_id(
        payment_id=payment_id,
    )

    return bool(
        payment
        and payment["status"] == "pending"
    )
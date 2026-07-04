# ==============================================
# 💳 ORDER PAYMENTS SERVICE
# Business Logic Layer
# ==============================================

from app.core.logger import logger

from app.repositories.order_payments_repo import (
    create_order_payment,
    get_order_payment,
    get_order_payments,
    get_payment_by_reference,
    mark_payment_paid,
    mark_payment_failed,
    mark_payment_cancelled,
    delete_order_payment,
)

from app.repositories.orders_repo import (
    get_order,
)

from app.repositories.restaurant_payment_settings_repo import (
    get_restaurant_payment_settings,
)

# ==============================================
# 🧩 CONSTANTS (DEFAULT VALUES)
# ==============================================

# القيم الافتراضية إذا لم توجد إعدادات للمطعم
DEFAULT_ALLOWED_METHODS = {
    "cash",
    "card",
}

# ==============================================
# 💳 PAYMENT VALIDATION
# Internal Helper
# ==============================================

async def _get_allowed_payment_methods(
    *,
    restaurant_id: int,
) -> set[str]:
    """
    جلب طرق الدفع المسموح بها لمطعم معين
    """
    settings = await get_restaurant_payment_settings(
        restaurant_id=restaurant_id,
    )
    
    # 🏦 إذا لم توجد إعدادات، نستخدم القيم الافتراضية
    if not settings:
        return DEFAULT_ALLOWED_METHODS.copy()  # cash, card فقط
    
    # 📋 بناء القائمة من إعدادات المطعم
    allowed = set()
    
    if settings.get("allow_cash", False):
        allowed.add("cash")
    
    if settings.get("allow_card", False):
        allowed.add("card")
    
    if settings.get("allow_ccp", False):
        allowed.add("ccp")
    
    if settings.get("allow_baridimob", False):
        allowed.add("baridimob")
    
    if settings.get("allow_stripe", False):
        allowed.add("stripe")
    
    if settings.get("allow_paypal", False):
        allowed.add("paypal")
    
    # إذا لم توجد أي طريقة مسموحة، نعود للقيم الافتراضية
    if not allowed:
        return DEFAULT_ALLOWED_METHODS.copy()
    
    return allowed

# ==============================================
# 💳 VALIDATE PAYMENT METHOD FOR ORDER
# ==============================================

async def validate_payment_method_for_order(
    *,
    order_id: int,
    payment_method: str,
) -> None:
    """
    التحقق من صحة طريقة الدفع لطلب معين
    
    Args:
        order_id: معرف الطلب
        payment_method: طريقة الدفع
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو طريقة الدفع غير مسموح بها
    """
    # جلب الطلب
    order = await get_order(
        order_id=order_id,
    )
    
    if not order:
        raise ValueError(
            "order_not_found",
        )
    
    # الحصول على معرف المطعم
    restaurant_id = order["restaurant_id"]
    
    # جلب طرق الدفع المسموح بها للمطعم
    allowed_methods = await _get_allowed_payment_methods(
        restaurant_id=restaurant_id,
    )
    
    # التحقق من صحة طريقة الدفع
    payment_method = str(
        payment_method,
    ).lower()
    
    if payment_method not in allowed_methods:
        raise ValueError(
            f"payment_method_not_allowed_{payment_method}",
        )
    
    return None

# ==============================================
# ➕ CREATE PAYMENT
# ==============================================

async def create_payment(
    *,
    order_id: int,
    payment_method: str,
    amount: float,
    transaction_reference: str | None = None,
) -> int:
    """
    إنشاء دفعة جديدة
    
    Args:
        order_id: معرف الطلب
        payment_method: طريقة الدفع
        amount: المبلغ
        transaction_reference: مرجع المعاملة (اختياري)
        
    Returns:
        int: معرف الدفعة الجديدة
        
    Raises:
        ValueError: إذا كان المبلغ غير صحيح أو طريقة الدفع غير مسموح بها
    """
    if amount <= 0:
        raise ValueError(
            "invalid_payment_amount",
        )
    
    # التحقق من صحة طريقة الدفع للطلب
    await validate_payment_method_for_order(
        order_id=order_id,
        payment_method=payment_method,
    )
    
    payment_id = await create_order_payment(
        order_id=order_id,
        payment_method=payment_method,
        payment_status="pending",
        amount=amount,
        transaction_reference=transaction_reference,
    )
    
    logger.info(
        "order_payment_created",
        extra={
            "payment_id": payment_id,
            "order_id": order_id,
        },
    )
    
    return payment_id

# ==============================================
# 🔍 GET ALLOWED PAYMENT METHODS FOR ORDER
# ==============================================

async def get_allowed_payment_methods_for_order(
    *,
    order_id: int,
) -> set[str]:
    """
    جلب طرق الدفع المسموح بها لطلب معين
    
    Args:
        order_id: معرف الطلب
        
    Returns:
        set[str]: مجموعة طرق الدفع المسموح بها
    """
    # جلب الطلب
    order = await get_order(
        order_id=order_id,
    )
    
    if not order:
        return set()
    
    # الحصول على معرف المطعم
    restaurant_id = order["restaurant_id"]
    
    # جلب طرق الدفع المسموح بها للمطعم
    return await _get_allowed_payment_methods(
        restaurant_id=restaurant_id,
    )

# ==============================================
# 🔍 GET ALLOWED PAYMENT METHODS BY RESTAURANT
# ==============================================

async def get_allowed_payment_methods_by_restaurant(
    *,
    restaurant_id: int,
) -> set[str]:
    """
    جلب طرق الدفع المسموح بها لمطعم
    
    Args:
        restaurant_id: معرف المطعم
        
    Returns:
        set[str]: مجموعة طرق الدفع المسموح بها
    """
    return await _get_allowed_payment_methods(
        restaurant_id=restaurant_id,
    )

# ==============================================
# ✅ CONFIRM PAYMENT
# ==============================================

async def confirm_payment(
    *,
    payment_id: int,
) -> None:
    """تأكيد دفعة"""
    
    payment = await get_order_payment(
        payment_id=payment_id,
    )
    
    if not payment:
        raise ValueError(
            "payment_not_found",
        )
    
    status = payment["payment_status"]
    
    if status == "paid":
        logger.info(
            "payment_already_paid",
            extra={
                "payment_id": payment_id,
            },
        )
        return
    
    if status == "cancelled":
        raise ValueError(
            "cannot_confirm_cancelled_payment",
        )
    
    if status == "failed":
        raise ValueError(
            "cannot_confirm_failed_payment",
        )
    
    await mark_payment_paid(
        payment_id=payment_id,
    )
    
    logger.info(
        "order_payment_confirmed",
        extra={
            "payment_id": payment_id,
        },
    )

# ==============================================
# ❌ FAIL PAYMENT
# ==============================================

async def fail_payment(
    *,
    payment_id: int,
) -> None:
    """فشل دفعة"""
    
    payment = await get_order_payment(
        payment_id=payment_id,
    )
    
    if not payment:
        raise ValueError(
            "payment_not_found",
        )
    
    status = payment["payment_status"]
    
    if status == "paid":
        raise ValueError(
            "cannot_fail_paid_payment",
        )
    
    if status == "cancelled":
        raise ValueError(
            "cannot_fail_cancelled_payment",
        )
    
    if status == "failed":
        logger.info(
            "payment_already_failed",
            extra={
                "payment_id": payment_id,
            },
        )
        return
    
    await mark_payment_failed(
        payment_id=payment_id,
    )
    
    logger.info(
        "order_payment_failed",
        extra={
            "payment_id": payment_id,
        },
    )

# ==============================================
# 🚫 CANCEL PAYMENT
# ==============================================

async def cancel_payment(
    *,
    payment_id: int,
) -> None:
    """إلغاء دفعة"""
    
    payment = await get_order_payment(
        payment_id=payment_id,
    )
    
    if not payment:
        raise ValueError(
            "payment_not_found",
        )
    
    status = payment["payment_status"]
    
    if status == "paid":
        raise ValueError(
            "cannot_cancel_paid_payment",
        )
    
    if status == "failed":
        raise ValueError(
            "cannot_cancel_failed_payment",
        )
    
    if status == "cancelled":
        logger.info(
            "payment_already_cancelled",
            extra={
                "payment_id": payment_id,
            },
        )
        return
    
    await mark_payment_cancelled(
        payment_id=payment_id,
    )
    
    logger.info(
        "order_payment_cancelled",
        extra={
            "payment_id": payment_id,
        },
    )

# ==============================================
# 🗑 DELETE PAYMENT
# ==============================================

async def remove_payment(
    *,
    payment_id: int,
) -> None:
    """حذف دفعة"""
    
    payment = await get_order_payment(
        payment_id=payment_id,
    )
    
    if not payment:
        raise ValueError(
            "payment_not_found",
        )
    
    await delete_order_payment(
        payment_id=payment_id,
    )
    
    logger.info(
        "order_payment_removed",
        extra={
            "payment_id": payment_id,
        },
    )

# ==============================================
# 🔍 IS PAYMENT PAID
# ==============================================

async def is_paid(
    *,
    payment_id: int,
) -> bool:
    """التحقق من حالة الدفعة (مدفوعة أم لا)"""
    
    payment = await get_order_payment(
        payment_id=payment_id,
    )
    
    return bool(
        payment
        and payment["payment_status"] == "paid",
    )

# ==============================================
# 🔍 IS PAYMENT PENDING
# ==============================================

async def is_pending(
    *,
    payment_id: int,
) -> bool:
    """التحقق من حالة الدفعة (معلقة أم لا)"""
    
    payment = await get_order_payment(
        payment_id=payment_id,
    )
    
    return bool(
        payment
        and payment["payment_status"] == "pending",
    )
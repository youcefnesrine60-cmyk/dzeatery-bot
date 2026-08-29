# ==============================================
# 📦 ORDERS SERVICE - PAID
# الدفع (mark_order_paid, is_order_paid)
# ==============================================

from typing import (
    Any,
    Dict,
)

from sqlalchemy.ext.asyncio import AsyncSession

# ✅ استيراد الاستثناءات
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
)

from app.core.logger import logger
from app.repositories.order_payments_repo import OrderPaymentsRepository
from app.repositories.orders_repo import OrdersRepository
from app.repositories.order_status_history_repo import (
    OrderStatusHistoryRepository,
)

# ==============================================
# 🧩 CONSTANTS
# ==============================================

# الحالات التي تعتبر مدفوعة
PAID_STATUSES = {"paid", "completed", "delivered"}

# الحالات التي لا يمكن تغييرها بعد الدفع
LOCKED_AFTER_PAID = {"completed", "delivered", "cancelled"}


# ==============================================
# 🧩 TYPES
# ==============================================

PaymentStatusInfo = Dict[str, Any]


# ==============================================
# 💰 MARK ORDER AS PAID
# ==============================================

async def mark_order_paid(
    *,
    order_id: int,
    payment_id: int,
    session: AsyncSession,
) -> None:
    """
    تحديد الطلب كمدفوع.
    
    Args:
        order_id: معرف الطلب
        payment_id: معرف الدفعة
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على الطلب أو الدفعة
        ValidationError: إذا كانت الدفعة لا تخص الطلب أو تم الدفع مسبقاً
    """
    logger.info(
        "mark_order_paid_started",
        extra={
            "order_id": order_id,
            "payment_id": payment_id,
        },
    )

    # 1️⃣ جلب الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "mark_order_paid_order_not_found",
            extra={"order_id": order_id},
        )
        raise NotFoundError(
            message=f"الطلب بـ ID '{order_id}' غير موجود",
        )

    # 2️⃣ جلب الدفعة
    payments_repo = OrderPaymentsRepository(session=session)
    payment = await payments_repo.get_by_id(id=payment_id)

    if not payment:
        logger.error(
            "mark_order_paid_payment_not_found",
            extra={"payment_id": payment_id},
        )
        raise NotFoundError(
            message=f"الدفعة بـ ID '{payment_id}' غير موجودة",
        )

    # 3️⃣ التحقق من أن الدفعة تخص هذا الطلب
    if payment.order_id != order_id:
        logger.error(
            "mark_order_paid_payment_not_belong_to_order",
            extra={
                "order_id": order_id,
                "payment_id": payment_id,
                "payment_order_id": payment.order_id,
            },
        )
        raise ValidationError(
            message=f"الدفعة '{payment_id}' لا تخص الطلب '{order_id}'",
        )

    # 4️⃣ التحقق من أن الدفعة ليست مدفوعة بالفعل
    if payment.payment_status == "paid":
        logger.info(
            "order_already_paid",
            extra={
                "order_id": order_id,
                "payment_id": payment_id,
            },
        )
        return

    # 5️⃣ تحديث حالة الدفعة إلى مدفوعة
    await payments_repo.mark_paid(payment_id=payment_id)

    # 6️⃣ تحديث حالة الطلب (إذا لم يكن في حالة نهائية)
    current_status = order.status

    if current_status not in LOCKED_AFTER_PAID:
        # تحديث حالة الطلب
        await orders_repo.update(
            id=order_id,
            data={
                "status": "paid",
                "is_paid": True,
            },
        )

        # إنشاء سجل في تاريخ الحالة
        history_repo = OrderStatusHistoryRepository(session=session)
        await history_repo.create(
            data={
                "order_id": order_id,
                "status": "paid",
                "employee_id": None,
                "note": f"تم دفع الطلب عبر الدفعة #{payment_id}",
            },
        )

        logger.info(
            "order_status_updated_to_paid",
            extra={
                "order_id": order_id,
                "previous_status": current_status,
            },
        )
    else:
        logger.info(
            "order_status_not_updated",
            extra={
                "order_id": order_id,
                "current_status": current_status,
                "reason": "order_in_final_state",
            },
        )

    logger.info(
        "order_marked_paid_successfully",
        extra={
            "order_id": order_id,
            "payment_id": payment_id,
        },
    )


# ==============================================
# 🔍 CHECK IF ORDER IS PAID
# ==============================================

async def is_order_paid(
    *,
    order_id: int,
    session: AsyncSession,
) -> bool:
    """
    التحقق من أن الطلب مدفوع.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        bool: True إذا كان الطلب مدفوعاً، False وإلا
    """
    logger.info(
        "is_order_paid_started",
        extra={"order_id": order_id},
    )

    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.warning(
            "is_order_paid_order_not_found",
            extra={"order_id": order_id},
        )
        return False

    # التحقق من الحالة المدفوعة
    is_paid = order.status in PAID_STATUSES or order.is_paid

    logger.info(
        "is_order_paid_result",
        extra={
            "order_id": order_id,
            "status": order.status,
            "is_paid": is_paid,
        },
    )

    return is_paid


# ==============================================
# 🔍 GET ORDER PAYMENT STATUS
# ==============================================

async def get_order_payment_status(
    *,
    order_id: int,
    session: AsyncSession,
) -> PaymentStatusInfo:
    """
    الحصول على حالة الدفع للطلب.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        PaymentStatusInfo: قاموس معلومات حالة الدفع
    """
    logger.info(
        "get_order_payment_status_started",
        extra={"order_id": order_id},
    )

    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.warning(
            "get_order_payment_status_order_not_found",
            extra={"order_id": order_id},
        )
        return {
            "order_id": order_id,
            "exists": False,
            "is_paid": False,
            "status": None,
            "payment_count": 0,
            "total_paid_amount": 0.0,
            "paid_payment_id": None,
            "remaining_amount": 0.0,
        }

    # جلب مدفوعات الطلب
    payments_repo = OrderPaymentsRepository(session=session)
    payments = await payments_repo.get_by_order_id(
        order_id=order_id,
        limit=1000,
    )

    # حساب المبالغ
    total_amount = order.total_amount or 0
    total_paid_amount = 0.0
    paid_payment_id = None

    for payment in payments:
        if payment.payment_status == "paid":
            total_paid_amount += payment.amount
            paid_payment_id = paid_payment_id or payment.id

    remaining_amount = max(0, total_amount - total_paid_amount)

    return {
        "order_id": order_id,
        "exists": len(payments) > 0,
        "is_paid": total_paid_amount >= total_amount and total_amount > 0,
        "status": order.status,
        "payment_count": len(payments),
        "total_paid_amount": round(total_paid_amount, 2),
        "remaining_amount": round(remaining_amount, 2),
        "paid_payment_id": paid_payment_id,
    }


# ==============================================
# 💰 UNPAY ORDER
# ==============================================

async def unpay_order(
    *,
    order_id: int,
    session: AsyncSession,
) -> None:
    """
    إلغاء حالة الدفع للطلب (إلغاء تعيين is_paid).
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على الطلب
        ValidationError: إذا كان الطلب في حالة نهائية
    """
    logger.info(
        "unpay_order_started",
        extra={"order_id": order_id},
    )

    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "unpay_order_order_not_found",
            extra={"order_id": order_id},
        )
        raise NotFoundError(
            message=f"الطلب بـ ID '{order_id}' غير موجود",
        )

    # التحقق من أن الطلب ليس في حالة نهائية
    if order.status in LOCKED_AFTER_PAID:
        raise ValidationError(
            message=f"لا يمكن إلغاء الدفع للطلب في حالة '{order.status}'",
        )

    # تحديث حالة الطلب
    await orders_repo.update(
        id=order_id,
        data={
            "is_paid": False,
        },
    )

    # إنشاء سجل في تاريخ الحالة
    history_repo = OrderStatusHistoryRepository(session=session)
    await history_repo.create(
        data={
            "order_id": order_id,
            "status": order.status,
            "employee_id": None,
            "note": "تم إلغاء حالة الدفع للطلب",
        },
    )

    logger.info(
        "order_unpaid_successfully",
        extra={"order_id": order_id},
    )


# ==============================================
# 💰 PROCESS PAYMENT FOR ORDER
# ==============================================

async def process_order_payment(
    *,
    order_id: int,
    payment_method: str,
    amount: float,
    session: AsyncSession,
) -> int:
    """
    معالجة الدفع للطلب وإنشاء دفعة جديدة.
    
    Args:
        order_id: معرف الطلب
        payment_method: طريقة الدفع
        amount: المبلغ
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        int: معرف الدفعة المنشأة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على الطلب
        ValidationError: إذا كان المبلغ غير صالح أو الطلب مدفوع
    """
    from app.services.business.order_payments_service import OrderPaymentsService

    logger.info(
        "process_order_payment_started",
        extra={
            "order_id": order_id,
            "payment_method": payment_method,
            "amount": amount,
        },
    )

    # التحقق من وجود الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        raise NotFoundError(
            message=f"الطلب بـ ID '{order_id}' غير موجود",
        )

    # التحقق من أن الطلب ليس مدفوعاً
    if order.is_paid:
        raise ValidationError(
            message=f"الطلب #{order.order_number} مدفوع بالفعل",
        )

    # التحقق من المبلغ
    if amount <= 0:
        raise ValidationError(
            message="المبلغ يجب أن يكون أكبر من الصفر",
        )

    # إنشاء دفعة جديدة
    payment_service = OrderPaymentsService(session=session)

    from app.schemas.payment import PaymentCreate

    payment_data = PaymentCreate(
        order_id=order_id,
        payment_method=payment_method,
        amount=amount,
    )

    payment = await payment_service.create_payment(
        payment_data=payment_data,
    )

    # تحديد الطلب كمدفوع إذا كان المبلغ كافياً
    if amount >= (order.total_amount or 0):
        await mark_order_paid(
            order_id=order_id,
            payment_id=payment.id,
            session=session,
        )

    logger.info(
        "order_payment_processed",
        extra={
            "order_id": order_id,
            "payment_id": payment.id,
            "amount": amount,
        },
    )

    return payment.id


# ==============================================
# 🔄 COMPATIBILITY FUNCTIONS
# ==============================================

# دوال التوافق مع الإصدار القديم
async def mark_order_paid_compat(
    *,
    order_id: int,
    payment_id: int,
    session: AsyncSession,
) -> None:
    """
    دالة متوافقة مع الإصدار القديم (مغلفة).
    
    Args:
        order_id: معرف الطلب
        payment_id: معرف الدفعة
        session: جلسة قاعدة البيانات غير المتزامنة
    """
    await mark_order_paid(
        order_id=order_id,
        payment_id=payment_id,
        session=session,
    )


async def is_order_paid_compat(
    *,
    order_id: int,
    session: AsyncSession,
) -> bool:
    """
    دالة متوافقة مع الإصدار القديم (مغلفة).
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        bool: True إذا كان الطلب مدفوعاً
    """
    return await is_order_paid(
        order_id=order_id,
        session=session,
    )
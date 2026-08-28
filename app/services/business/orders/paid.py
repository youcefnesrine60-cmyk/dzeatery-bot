# ==============================================
# 📦 ORDERS SERVICE - PAID
# الدفع (mark_order_paid, is_order_paid)
# ==============================================

from typing import (
    Any,
    Dict,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.repositories.order_payments_repo import OrderPaymentsRepository
from app.repositories.orders_repo import OrdersRepository
from app.repositories.order_status_history_repo import (
    OrderStatusHistoryRepository,
)

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
        payment_id: معرف الدفع
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو الدفع أو الدفع لا يخص هذا الطلب
    """
    logger.info(
        "mark_order_paid_started",
        extra={
            "order_id": order_id,
            "payment_id": payment_id,
        },
    )

    # جلب الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "mark_order_paid_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # جلب الدفعة
    payments_repo = OrderPaymentsRepository(session=session)
    payment = await payments_repo.get_by_id(id=payment_id)

    if not payment:
        logger.error(
            "mark_order_paid_payment_not_found",
            extra={"payment_id": payment_id},
        )
        raise ValueError("payment_not_found")

    # التحقق من أن الدفعة تخص هذا الطلب
    if payment.order_id != order_id:
        logger.error(
            "mark_order_paid_payment_not_belong_to_order",
            extra={
                "order_id": order_id,
                "payment_id": payment_id,
                "payment_order_id": payment.order_id,
            },
        )
        raise ValueError("payment_not_belong_to_order")

    # التحقق من أن الدفعة ليست مدفوعة بالفعل
    if payment.payment_status == "paid":
        logger.info(
            "order_already_paid",
            extra={
                "order_id": order_id,
                "payment_id": payment_id,
            },
        )
        return

    # تحديث حالة الدفعة إلى مدفوعة
    await payments_repo.mark_paid(payment_id=payment_id)

    # تحديث حالة الطلب إلى "paid" (إذا لم يكن في حالة نهائية)
    current_status = order.status

    if current_status not in {"completed", "cancelled", "delivered"}:
        await orders_repo.update_status(
            order_id=order_id,
            status="paid",
        )

        # إنشاء سجل في تاريخ الحالة
        history_repo = OrderStatusHistoryRepository(session=session)

        await history_repo.create(
            data={
                "order_id": order_id,
                "old_status": current_status,
                "new_status": "paid",
                "changed_by_employee_id": None,
                "note": "order_paid",
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
        True إذا كان الطلب مدفوعاً، False وإلا
    """
    logger.info(
        "is_order_paid_started",
        extra={"order_id": order_id},
    )

    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.info(
            "is_order_paid_order_not_found",
            extra={"order_id": order_id},
        )
        return False

    # الحالات التي تعتبر مدفوعة
    paid_statuses = {"paid", "completed", "delivered"}
    is_paid = order.status in paid_statuses

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
        قاموس معلومات حالة الدفع
    """
    logger.info(
        "get_order_payment_status_started",
        extra={"order_id": order_id},
    )

    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.info(
            "get_order_payment_status_order_not_found",
            extra={"order_id": order_id},
        )
        return {
            "order_id": order_id,
            "exists": False,
            "is_paid": False,
            "status": None,
        }

    # جلب مدفوعات الطلب
    payments_repo = OrderPaymentsRepository(session=session)
    payments = await payments_repo.get_by_order_id(order_id=order_id)

    # التحقق من وجود دفعة مدفوعة
    paid_payment = None

    for payment in payments:
        if payment.payment_status == "paid":
            paid_payment = payment
            break

    return {
        "order_id": order_id,
        "exists": len(payments) > 0,
        "is_paid": paid_payment is not None,
        "status": order.status,
        "payment_count": len(payments),
        "paid_payment_id": paid_payment.id if paid_payment else None,
        "total_paid_amount": sum(
            p.amount for p in payments if p.payment_status == "paid"
        ),
    }
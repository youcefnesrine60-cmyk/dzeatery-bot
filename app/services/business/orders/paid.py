# ==============================================
# 📦 ORDERS SERVICE - PAID
# الدفع (mark_order_paid)
# ==============================================

from app.core.logger import logger

from app.repositories.orders_repo import (
    get_order,
    update_order_status,
)

from app.repositories.order_payments_repo import (
    get_order_payment,
    mark_payment_paid,
)

from app.repositories.order_status_history_repo import (
    create_status_history,
)

# ==============================================
# 💰 MARK ORDER AS PAID
# ==============================================

async def mark_order_paid(
    *,
    order_id: int,
    payment_id: int,
) -> None:
    """
    تحديد الطلب كمدفوع
    
    Args:
        order_id: معرف الطلب
        payment_id: معرف الدفع
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو الدفع
    """
    # جلب الطلب
    order = await get_order(
        order_id=order_id,
    )
    
    if not order:
        raise ValueError(
            "order_not_found",
        )
    
    # جلب الدفعة
    payment = await get_order_payment(
        payment_id=payment_id,
    )
    
    if not payment:
        raise ValueError(
            "payment_not_found",
        )
    
    # التحقق من أن الدفعة تخص هذا الطلب
    if payment["order_id"] != order_id:
        raise ValueError(
            "payment_not_belong_to_order",
        )
    
    # التحقق من أن الدفعة ليست مدفوعة بالفعل
    if payment["payment_status"] == "paid":
        logger.info(
            "order_already_paid",
            extra={
                "order_id": order_id,
                "payment_id": payment_id,
            },
        )
        return
    
    # تحديث حالة الدفعة إلى مدفوعة
    await mark_payment_paid(
        payment_id=payment_id,
    )
    
    # تحديث حالة الطلب إلى "paid" (إذا لم يكن في حالة نهائية)
    current_status = str(
        order["status"],
    )
    
    if current_status not in {"completed", "cancelled", "delivered"}:
        await update_order_status(
            order_id=order_id,
            status="paid",
        )
        
        await create_status_history(
            order_id=order_id,
            old_status=current_status,
            new_status="paid",
            changed_by_employee_id=None,
            note="order_paid",
        )
    
    logger.info(
        "order_marked_paid",
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
) -> bool:
    """
    التحقق من أن الطلب مدفوع
    
    Args:
        order_id: معرف الطلب
        
    Returns:
        bool: True إذا كان الطلب مدفوعاً، False وإلا
    """
    order = await get_order(
        order_id=order_id,
    )
    
    if not order:
        return False
    
    status = str(
        order.get(
            "status",
            "",
        ),
    )
    
    return status in {"paid", "completed", "delivered"}
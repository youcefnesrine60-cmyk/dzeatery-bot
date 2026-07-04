# ==============================================
# 📦 ORDERS SERVICE - UPDATE
# تحديث الطلب (change_order_status, 
# recalculate_order_totals)
# ==============================================

from app.core.logger import logger

from app.repositories.orders_repo import (
    get_order,
    update_order_status,
    update_order_totals,
)

from app.repositories.order_status_history_repo import (
    create_status_history,
)

from app.services.business.orders.helpers import check_order_editable

# ==============================================
# 🔄 CHANGE ORDER STATUS
# ==============================================

async def change_order_status(
    *,
    order_id: int,
    new_status: str,
    employee_id: int | None = None,
    note: str | None = None,
) -> None:
    """
    تغيير حالة الطلب
    
    Args:
        order_id: معرف الطلب
        new_status: الحالة الجديدة
        employee_id: معرف الموظف (اختياري)
        note: ملاحظة (اختياري)
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب
    """
    order = await get_order(
        order_id=order_id,
    )

    if not order:
        raise ValueError(
            "order_not_found",
        )

    old_status = str(
        order["status"],
    )

    if old_status == new_status:
        return

    await update_order_status(
        order_id=order_id,
        status=new_status,
    )

    await create_status_history(
        order_id=order_id,
        old_status=old_status,
        new_status=new_status,
        changed_by_employee_id=employee_id,
        note=note,
    )

    logger.info(
        "order_status_changed",
        extra={
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status,
        },
    )

# ==============================================
# 💰 UPDATE TOTALS
# ==============================================

async def recalculate_order_totals(
    *,
    order_id: int,
    subtotal_amount: float,
    discount_amount: float,
    tax_amount: float,
    delivery_amount: float,
    total_amount: float,
) -> None:
    """
    تحديث إجماليات الطلب
    
    Args:
        order_id: معرف الطلب
        subtotal_amount: المجموع الفرعي
        discount_amount: مبلغ الخصم
        tax_amount: مبلغ الضريبة
        delivery_amount: مبلغ التوصيل
        total_amount: المجموع الكلي
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو كان مقفلاً
    """
    order = await get_order(
        order_id=order_id,
    )

    if not order:
        raise ValueError(
            "order_not_found",
        )

    await check_order_editable(
        order=order,
    )

    await update_order_totals(
        order_id=order_id,
        subtotal_amount=subtotal_amount,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        delivery_amount=delivery_amount,
        total_amount=total_amount,
    )

    logger.info(
        "order_totals_updated",
        extra={
            "order_id": order_id,
        },
    )
# ==============================================
# 📦 ORDERS SERVICE - UPDATE
# تحديث الطلب 
# (change_order_status, recalculate_order_totals)
# ==============================================

from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.order import Order
from app.repositories.orders_repo import OrdersRepository
from app.repositories.order_status_history_repo import (
    OrderStatusHistoryRepository,
)
from app.services.business.orders.helpers import check_order_editable

# ==============================================
# 🧩 TYPES
# ==============================================

OrderTotals = Tuple[float, float, float, float, float]
OrderUpdateData = Dict[str, Any]

# ==============================================
# 🔄 CHANGE ORDER STATUS
# ==============================================

async def change_order_status(
    *,
    order_id: int,
    new_status: str,
    employee_id: Optional[int] = None,
    note: Optional[str] = None,
    session: AsyncSession,
) -> Order:
    """
    تغيير حالة الطلب.
    
    Args:
        order_id: معرف الطلب
        new_status: الحالة الجديدة
        employee_id: معرف الموظف (اختياري)
        note: ملاحظة (اختياري)
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المُحدّث
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "change_order_status_started",
        extra={
            "order_id": order_id,
            "new_status": new_status,
            "employee_id": employee_id,
        },
    )

    # جلب الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "change_order_status_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    old_status = order.status

    # إذا كانت الحالة نفسها، لا تفعل شيئاً
    if old_status == new_status:
        logger.info(
            "change_order_status_same_status",
            extra={
                "order_id": order_id,
                "status": new_status,
            },
        )
        return order

    # تحديث حالة الطلب
    updated_order = await orders_repo.update_status(
        order_id=order_id,
        status=new_status,
    )

    if not updated_order:
        logger.error(
            "change_order_status_update_failed",
            extra={"order_id": order_id},
        )
        raise ValueError("order_update_failed")

    # إنشاء سجل في تاريخ الحالة
    history_repo = OrderStatusHistoryRepository(session=session)

    await history_repo.create(
        data={
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status,
            "changed_by_employee_id": employee_id,
            "note": note,
        },
    )

    logger.info(
        "order_status_changed_successfully",
        extra={
            "order_id": order_id,
            "old_status": old_status,
            "new_status": new_status,
            "employee_id": employee_id,
        },
    )

    return updated_order


# ==============================================
# 💰 UPDATE ORDER TOTALS
# ==============================================

async def update_order_totals(
    *,
    order_id: int,
    subtotal_amount: float,
    discount_amount: float,
    tax_amount: float,
    delivery_amount: float,
    total_amount: float,
    session: AsyncSession,
) -> Order:
    """
    تحديث إجماليات الطلب.
    
    Args:
        order_id: معرف الطلب
        subtotal_amount: المجموع الفرعي
        discount_amount: مبلغ الخصم
        tax_amount: مبلغ الضريبة
        delivery_amount: مبلغ التوصيل
        total_amount: المجموع الكلي
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المُحدّث
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو كان مقفلاً
    """
    logger.info(
        "update_order_totals_started",
        extra={
            "order_id": order_id,
            "subtotal_amount": subtotal_amount,
            "total_amount": total_amount,
        },
    )

    # جلب الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "update_order_totals_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # التحقق من إمكانية التعديل
    check_order_editable(order)

    # تحديث الإجماليات
    updated_order = await orders_repo.update_totals(
        order_id=order_id,
        subtotal_amount=subtotal_amount,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        delivery_amount=delivery_amount,
        total_amount=total_amount,
    )

    if not updated_order:
        logger.error(
            "update_order_totals_update_failed",
            extra={"order_id": order_id},
        )
        raise ValueError("order_update_failed")

    logger.info(
        "order_totals_updated_successfully",
        extra={
            "order_id": order_id,
            "subtotal_amount": subtotal_amount,
            "total_amount": total_amount,
        },
    )

    return updated_order


# ==============================================
# 🔄 RECALCULATE ORDER TOTALS
# ==============================================

async def recalculate_order_totals(
    *,
    order_id: int,
    session: AsyncSession,
) -> OrderTotals:
    """
    إعادة حساب إجماليات الطلب (جمع بين calculate و update).
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        (subtotal, discount, tax, delivery, total)
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب
    """
    from app.services.business.orders.totals import calculate_order_totals

    logger.info(
        "recalculate_order_totals_started",
        extra={"order_id": order_id},
    )

    # حساب وتحديث الإجماليات
    totals = await calculate_order_totals(
        order_id=order_id,
        session=session,
    )

    logger.info(
        "recalculate_order_totals_completed",
        extra={
            "order_id": order_id,
            "subtotal": totals[0],
            "total": totals[4],
        },
    )

    return totals


# ==============================================
# ✅ UPDATE ORDER
# ==============================================

async def update_order(
    *,
    order_id: int,
    data: OrderUpdateData,
    session: AsyncSession,
) -> Order:
    """
    تحديث بيانات الطلب العامة.
    
    Args:
        order_id: معرف الطلب
        data: بيانات التحديث
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المُحدّث
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو كان مقفلاً
    """
    logger.info(
        "update_order_started",
        extra={
            "order_id": order_id,
            "fields": list(data.keys()),
        },
    )

    # جلب الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "update_order_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # التحقق من إمكانية التعديل
    check_order_editable(order)

    # تحديث الطلب
    updated_order = await orders_repo.update(
        id=order_id,
        data=data,
    )

    if not updated_order:
        logger.error(
            "update_order_update_failed",
            extra={"order_id": order_id},
        )
        raise ValueError("order_update_failed")

    logger.info(
        "update_order_successfully",
        extra={
            "order_id": order_id,
            "fields": list(data.keys()),
        },
    )

    return updated_order
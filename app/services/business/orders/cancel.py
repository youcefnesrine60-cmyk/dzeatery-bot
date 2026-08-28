# ==============================================
# 📦 ORDERS SERVICE - CANCEL
# إلغاء الطلب (cancel_order)
# ==============================================

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.repositories.orders_repo import OrdersRepository
from app.services.business.orders.update import change_order_status

# ==============================================
# ❌ CANCEL ORDER
# ==============================================

async def cancel_order(
    *,
    order_id: int,
    employee_id: Optional[int] = None,
    reason: Optional[str] = None,
    session: AsyncSession,
) -> None:
    """
    إلغاء الطلب.
    
    Args:
        order_id: معرف الطلب
        employee_id: معرف الموظف (اختياري)
        reason: سبب الإلغاء (اختياري)
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "cancel_order_started",
        extra={
            "order_id": order_id,
            "employee_id": employee_id,
            "reason": reason,
        },
    )

    # التحقق من وجود الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "cancel_order_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # تغيير حالة الطلب إلى cancelled
    await change_order_status(
        order_id=order_id,
        new_status="cancelled",
        employee_id=employee_id,
        note=reason or "Order cancelled",
        session=session,
    )

    logger.info(
        "order_cancelled_successfully",
        extra={
            "order_id": order_id,
            "employee_id": employee_id,
        },
    )
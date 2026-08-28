# ==============================================
# 📦 ORDERS SERVICE - COMPLETE
# إكمال الطلب (complete_order)
# ==============================================

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.repositories.orders_repo import OrdersRepository
from app.services.business.orders.update import change_order_status

# ==============================================
# 🧩 TYPES
# ==============================================


# ==============================================
# ✅ COMPLETE ORDER
# ==============================================

async def complete_order(
    *,
    order_id: int,
    employee_id: Optional[int] = None,
    note: Optional[str] = None,
    session: AsyncSession,
) -> None:
    """
    إكمال الطلب (تعيين الحالة إلى completed).
    
    Args:
        order_id: معرف الطلب
        employee_id: معرف الموظف (اختياري)
        note: ملاحظة إضافية (اختياري)
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "complete_order_started",
        extra={
            "order_id": order_id,
            "employee_id": employee_id,
            "note": note,
        },
    )

    # التحقق من وجود الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "complete_order_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # تغيير حالة الطلب إلى completed
    await change_order_status(
        order_id=order_id,
        new_status="completed",
        employee_id=employee_id,
        note=note or "Order completed",
        session=session,
    )

    logger.info(
        "order_completed_successfully",
        extra={
            "order_id": order_id,
            "employee_id": employee_id,
        },
    )
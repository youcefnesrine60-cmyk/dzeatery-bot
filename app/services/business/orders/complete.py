# ==============================================
# 📦 ORDERS SERVICE - COMPLETE
# إكمال الطلب (complete_order)
# ==============================================

from app.core.logger import logger

from app.repositories.orders_repo import (
    get_order,
)

from app.services.business.orders.update import change_order_status

# ==============================================
# ✅ COMPLETE ORDER
# ==============================================

async def complete_order(
    *,
    order_id: int,
    employee_id: int | None = None,
    note: str | None = None,
) -> None:
    """
    إكمال الطلب
    
    Args:
        order_id: معرف الطلب
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
    
    await change_order_status(
        order_id=order_id,
        new_status="completed",
        employee_id=employee_id,
        note=note or "Order completed",
    )
    
    logger.info(
        "order_completed",
        extra={
            "order_id": order_id,
        },
    )
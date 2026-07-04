# ==============================================
# 📦 ORDERS SERVICE - CANCEL
# إلغاء الطلب (cancel_order)
# ==============================================

from app.core.logger import logger

from app.repositories.orders_repo import (
    get_order,
)

from app.services.business.orders.update import change_order_status

# ==============================================
# ❌ CANCEL ORDER
# ==============================================

async def cancel_order(
    *,
    order_id: int,
    employee_id: int | None = None,
    reason: str | None = None,
) -> None:
    """
    إلغاء الطلب
    
    Args:
        order_id: معرف الطلب
        employee_id: معرف الموظف (اختياري)
        reason: سبب الإلغاء (اختياري)
        
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
        new_status="cancelled",
        employee_id=employee_id,
        note=reason or "Order cancelled",
    )
    
    logger.info(
        "order_cancelled",
        extra={
            "order_id": order_id,
        },
    )
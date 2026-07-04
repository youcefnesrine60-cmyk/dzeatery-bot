# ==============================================
# 📦 ORDERS SERVICE - DELETE
# حذف الطلب (remove_order)
# ==============================================

from app.core.logger import logger

from app.repositories.orders_repo import (
    get_order,
    delete_order,
)

from app.services.business.orders.helpers import check_order_editable

# ==============================================
# ❌ DELETE ORDER
# ==============================================

async def remove_order(
    *,
    order_id: int,
) -> None:
    """
    حذف طلب
    
    Args:
        order_id: معرف الطلب
        
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

    await delete_order(
        order_id=order_id,
    )

    logger.info(
        "order_removed",
        extra={
            "order_id": order_id,
        },
    )
# ==============================================
# 📦 ORDERS SERVICE - DELETE
# حذف الطلب (remove_order)
# ==============================================

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.repositories.orders_repo import OrdersRepository
from app.services.business.orders.helpers import check_order_editable

# ==============================================
# ❌ DELETE ORDER
# ==============================================

async def remove_order(
    *,
    order_id: int,
    session: AsyncSession,
) -> None:
    """
    حذف طلب.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو كان مقفلاً
    """
    logger.info(
        "remove_order_started",
        extra={"order_id": order_id},
    )

    # التحقق من وجود الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "remove_order_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # التحقق من إمكانية تعديل الطلب
    check_order_editable(order)

    # حذف الطلب
    await orders_repo.delete(id=order_id)

    logger.info(
        "order_removed_successfully",
        extra={
            "order_id": order_id,
        },
    )
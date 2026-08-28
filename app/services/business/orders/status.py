# ==============================================
# 📦 ORDERS SERVICE - STATUS HISTORY
# إدارة الحالات 
# (get_status_history, get_order_timeline, get_last_status)
# ==============================================

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.order_item import OrderStatusHistory
from app.repositories.order_status_history_repo import (
    OrderStatusHistoryRepository,
)

# ==============================================
# 🧩 TYPES
# ==============================================

StatusHistoryDict = Dict[str, Any]
StatusHistoryList = List[OrderStatusHistory]
StatusDistribution = Dict[str, int]

# ==============================================
# 📜 STATUS HISTORY
# ==============================================

async def get_status_history(
    *,
    order_id: int,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> StatusHistoryList:
    """
    جلب سجل حالات الطلب.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        
    Returns:
        قائمة سجل الحالات
    """
    logger.info(
        "get_status_history_started",
        extra={
            "order_id": order_id,
            "skip": skip,
            "limit": limit,
        },
    )

    history_repo = OrderStatusHistoryRepository(session=session)
    history = await history_repo.get_by_order_id(
        order_id=order_id,
        skip=skip,
        limit=limit,
    )

    logger.info(
        "get_status_history_retrieved",
        extra={
            "order_id": order_id,
            "count": len(history),
        },
    )

    return history


# ==============================================
# 📈 STATUS TIMELINE
# ==============================================

async def get_order_timeline(
    *,
    order_id: int,
    session: AsyncSession,
) -> List[Dict[str, Any]]:
    """
    جلب الخط الزمني لحالات الطلب.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        قائمة الخط الزمني
    """
    logger.info(
        "get_order_timeline_started",
        extra={"order_id": order_id},
    )

    history_repo = OrderStatusHistoryRepository(session=session)
    timeline = await history_repo.get_status_timeline(order_id=order_id)

    logger.info(
        "get_order_timeline_retrieved",
        extra={
            "order_id": order_id,
            "count": len(timeline),
        },
    )

    return timeline


# ==============================================
# 🔍 LAST STATUS CHANGE
# ==============================================

async def get_last_status(
    *,
    order_id: int,
    session: AsyncSession,
) -> Optional[OrderStatusHistory]:
    """
    جلب آخر تغيير في حالة الطلب.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        بيانات آخر تغيير أو None
    """
    logger.info(
        "get_last_status_started",
        extra={"order_id": order_id},
    )

    history_repo = OrderStatusHistoryRepository(session=session)
    last_status = await history_repo.get_last_status_change(order_id=order_id)

    if last_status:
        logger.info(
            "get_last_status_found",
            extra={
                "order_id": order_id,
                "new_status": last_status.new_status,
                "created_at": last_status.created_at,
            },
        )
    else:
        logger.info(
            "get_last_status_not_found",
            extra={"order_id": order_id},
        )

    return last_status


# ==============================================
# 🔍 GET STATUS HISTORY COUNT
# ==============================================

async def get_status_history_count(
    *,
    order_id: int,
    session: AsyncSession,
) -> int:
    """
    حساب عدد تغييرات حالة الطلب.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        عدد التغييرات
    """
    logger.info(
        "get_status_history_count_started",
        extra={"order_id": order_id},
    )

    history_repo = OrderStatusHistoryRepository(session=session)
    count = await history_repo.count_status_changes(order_id=order_id)

    logger.info(
        "get_status_history_count_result",
        extra={
            "order_id": order_id,
            "count": count,
        },
    )

    return count


# ==============================================
# 🔍 GET ORDERS REACHED STATUS
# ==============================================

async def get_orders_reached_status(
    *,
    status: str,
    session: AsyncSession,
) -> List[int]:
    """
    الحصول على معرفات الطلبات التي وصلت إلى حالة معينة.
    
    Args:
        status: حالة الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        قائمة معرفات الطلبات
    """
    logger.info(
        "get_orders_reached_status_started",
        extra={"status": status},
    )

    history_repo = OrderStatusHistoryRepository(session=session)
    order_ids = await history_repo.get_orders_reached_status(status=status)

    logger.info(
        "get_orders_reached_status_result",
        extra={
            "status": status,
            "count": len(order_ids),
        },
    )

    return order_ids


# ==============================================
# 📊 GET STATUS DISTRIBUTION
# ==============================================

async def get_status_distribution(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> StatusDistribution:
    """
    الحصول على توزيع حالات الطلبات لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        توزيع الحالات
    """
    logger.info(
        "get_status_distribution_started",
        extra={"restaurant_id": restaurant_id},
    )

    # جلب جميع الطلبات
    from app.repositories.orders_repo import OrdersRepository

    orders_repo = OrdersRepository(session=session)
    orders = await orders_repo.get_by_restaurant_id(
        restaurant_id=restaurant_id,
    )

    # حساب توزيع الحالات
    distribution: StatusDistribution = {}

    for order in orders:
        status = order.status
        distribution[status] = distribution.get(status, 0) + 1

    logger.info(
        "get_status_distribution_result",
        extra={
            "restaurant_id": restaurant_id,
            "distribution": distribution,
        },
    )

    return distribution
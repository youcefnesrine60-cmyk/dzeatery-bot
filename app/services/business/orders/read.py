# ==============================================
# 📦 ORDERS SERVICE - READ
# قراءة الطلبات 
# (get_restaurant_order, get_orders, get_orders_status)
# ==============================================

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.order import Order
from app.repositories.orders_repo import OrdersRepository

# ==============================================
# 🧩 TYPES
# ==============================================

OrderDict = Dict[str, Any]
OrderList = List[Order]

# ==============================================
# 🔍 GET ORDER
# ==============================================

async def get_restaurant_order(
    *,
    order_id: int,
    session: AsyncSession,
) -> Optional[Order]:
    """
    جلب بيانات طلب معين.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        كائن الطلب أو None
    """
    logger.info(
        "get_restaurant_order_started",
        extra={"order_id": order_id},
    )

    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if order:
        logger.info(
            "get_restaurant_order_found",
            extra={
                "order_id": order_id,
                "status": order.status,
            },
        )
    else:
        logger.info(
            "get_restaurant_order_not_found",
            extra={"order_id": order_id},
        )

    return order


# ==============================================
# 🔍 GET ORDER BY NUMBER
# ==============================================

async def get_order_by_number(
    *,
    restaurant_id: int,
    order_number: str,
    session: AsyncSession,
) -> Optional[Order]:
    """
    جلب طلب حسب رقمه.
    
    Args:
        restaurant_id: معرف المطعم
        order_number: رقم الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        كائن الطلب أو None
    """
    logger.info(
        "get_order_by_number_started",
        extra={
            "restaurant_id": restaurant_id,
            "order_number": order_number,
        },
    )

    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_order_number(
        restaurant_id=restaurant_id,
        order_number=order_number,
    )

    if order:
        logger.info(
            "get_order_by_number_found",
            extra={
                "restaurant_id": restaurant_id,
                "order_number": order_number,
                "order_id": order.id,
            },
        )
    else:
        logger.info(
            "get_order_by_number_not_found",
            extra={
                "restaurant_id": restaurant_id,
                "order_number": order_number,
            },
        )

    return order


# ==============================================
# 🔍 GET RESTAURANT ORDERS
# ==============================================

async def get_orders(
    *,
    restaurant_id: int,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> OrderList:
    """
    جلب جميع طلبات مطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        status: حالة الطلب (اختياري)
        
    Returns:
        قائمة الطلبات
    """
    logger.info(
        "get_orders_started",
        extra={
            "restaurant_id": restaurant_id,
            "skip": skip,
            "limit": limit,
            "status": status,
        },
    )

    orders_repo = OrdersRepository(session=session)
    orders = await orders_repo.get_by_restaurant_id(
        restaurant_id=restaurant_id,
        skip=skip,
        limit=limit,
        status=status,
    )

    logger.info(
        "get_orders_retrieved",
        extra={
            "restaurant_id": restaurant_id,
            "count": len(orders),
            "status": status,
        },
    )

    return orders


# ==============================================
# 🔍 GET ORDERS BY STATUS
# ==============================================

async def get_orders_by_status(
    *,
    restaurant_id: int,
    status: str,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> OrderList:
    """
    جلب طلبات مطعم حسب الحالة.
    
    Args:
        restaurant_id: معرف المطعم
        status: حالة الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        
    Returns:
        قائمة الطلبات
    """
    logger.info(
        "get_orders_by_status_started",
        extra={
            "restaurant_id": restaurant_id,
            "status": status,
            "skip": skip,
            "limit": limit,
        },
    )

    orders_repo = OrdersRepository(session=session)
    orders = await orders_repo.get_by_status(
        status=status,
        restaurant_id=restaurant_id,
        skip=skip,
        limit=limit,
    )

    logger.info(
        "get_orders_by_status_retrieved",
        extra={
            "restaurant_id": restaurant_id,
            "status": status,
            "count": len(orders),
        },
    )

    return orders


# ==============================================
# 🔍 GET ORDER WITH DETAILS
# ==============================================

async def get_order_with_details(
    *,
    order_id: int,
    session: AsyncSession,
) -> Optional[Order]:
    """
    جلب طلب مع جميع علاقاته (عناصر، خيارات، مدفوعات، تاريخ الحالة).
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        كائن الطلب مع العلاقات أو None
    """
    logger.info(
        "get_order_with_details_started",
        extra={"order_id": order_id},
    )

    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if order:
        # تحميل العلاقات (يتم تحميلها تلقائياً عبر lazy="selectin" في النموذج)
        logger.info(
            "get_order_with_details_found",
            extra={
                "order_id": order_id,
                "items_count": len(order.items) if order.items else 0,
                "payments_count": len(order.payments) if order.payments else 0,
            },
        )
    else:
        logger.info(
            "get_order_with_details_not_found",
            extra={"order_id": order_id},
        )

    return order


# ==============================================
# 🔢 COUNT ORDERS BY RESTAURANT
# ==============================================

async def count_orders_by_restaurant(
    *,
    restaurant_id: int,
    session: AsyncSession,
    status: Optional[str] = None,
) -> int:
    """
    حساب عدد طلبات مطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        status: حالة الطلب (اختياري)
        
    Returns:
        عدد الطلبات
    """
    logger.info(
        "count_orders_by_restaurant_started",
        extra={
            "restaurant_id": restaurant_id,
            "status": status,
        },
    )

    orders_repo = OrdersRepository(session=session)

    if status:
        count = await orders_repo.count_by_status(
            restaurant_id=restaurant_id,
            status=status,
        )
    else:
        count = await orders_repo.count_by_restaurant(
            restaurant_id=restaurant_id,
        )

    logger.info(
        "count_orders_by_restaurant_result",
        extra={
            "restaurant_id": restaurant_id,
            "status": status,
            "count": count,
        },
    )

    return count
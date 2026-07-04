# ==============================================
# 📦 ORDERS SERVICE - READ
# قراءة الطلبات (get_restaurant_order, 
# get_orders, get_orders_status)
# ==============================================

from app.repositories.orders_repo import (
    get_order,
    get_order_by_number,
    get_restaurant_orders,
    get_orders_by_status,
)

# ==============================================
# 🔍 GET ORDER
# ==============================================

async def get_restaurant_order(
    *,
    order_id: int,
) -> dict | None:
    """
    جلب بيانات طلب معين
    
    Args:
        order_id: معرف الطلب
        
    Returns:
        dict | None: بيانات الطلب أو None
    """
    return await get_order(
        order_id=order_id,
    )

# ==============================================
# 🔍 GET ORDER BY NUMBER
# ==============================================

async def get_order_number(
    *,
    restaurant_id: int,
    order_number: str,
) -> dict | None:
    """
    جلب طلب حسب رقمه
    
    Args:
        restaurant_id: معرف المطعم
        order_number: رقم الطلب
        
    Returns:
        dict | None: بيانات الطلب أو None
    """
    return await get_order_by_number(
        restaurant_id=restaurant_id,
        order_number=order_number,
    )

# ==============================================
# 🔍 GET RESTAURANT ORDERS
# ==============================================

async def get_orders(
    *,
    restaurant_id: int,
) -> list[dict]:
    """
    جلب جميع طلبات مطعم معين
    
    Args:
        restaurant_id: معرف المطعم
        
    Returns:
        list[dict]: قائمة الطلبات
    """
    return await get_restaurant_orders(
        restaurant_id=restaurant_id,
    )

# ==============================================
# 🔍 GET ORDERS BY STATUS
# ==============================================

async def get_orders_status(
    *,
    restaurant_id: int,
    status: str,
) -> list[dict]:
    """
    جلب طلبات مطعم حسب الحالة
    
    Args:
        restaurant_id: معرف المطعم
        status: حالة الطلب
        
    Returns:
        list[dict]: قائمة الطلبات
    """
    return await get_orders_by_status(
        restaurant_id=restaurant_id,
        status=status,
    )
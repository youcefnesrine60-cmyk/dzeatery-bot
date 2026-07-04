# ==============================================
# 📦 ORDERS SERVICE - STATUS HISTORY
# إدارة الحالات (get_status_history,
#  get_order_timeline, get_last_status)
# ==============================================

from app.repositories.order_status_history_repo import (
    get_order_status_history,
    get_last_status_change,
    get_status_timeline,
)

# ==============================================
# 📜 STATUS HISTORY
# ==============================================

async def get_status_history(
    *,
    order_id: int,
) -> list[dict]:
    """
    جلب سجل حالات الطلب
    
    Args:
        order_id: معرف الطلب
        
    Returns:
        list[dict]: قائمة سجل الحالات
    """
    return await get_order_status_history(
        order_id=order_id,
    )

# ==============================================
# 📈 STATUS TIMELINE
# ==============================================

async def get_order_timeline(
    *,
    order_id: int,
) -> list[dict]:
    """
    جلب الخط الزمني لحالات الطلب
    
    Args:
        order_id: معرف الطلب
        
    Returns:
        list[dict]: قائمة الخط الزمني
    """
    return await get_status_timeline(
        order_id=order_id,
    )

# ==============================================
# 🔍 LAST STATUS CHANGE
# ==============================================

async def get_last_status(
    *,
    order_id: int,
) -> dict | None:
    """
    جلب آخر تغيير في حالة الطلب
    
    Args:
        order_id: معرف الطلب
        
    Returns:
        dict | None: بيانات آخر تغيير أو None
    """
    return await get_last_status_change(
        order_id=order_id,
    )
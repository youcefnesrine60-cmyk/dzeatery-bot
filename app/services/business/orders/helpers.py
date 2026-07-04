# ==============================================
# 📦 ORDERS SERVICE - HELPERS
# الدوال المساعدة (_check_order_editable)
# ==============================================

from app.services.business.orders.constants import LOCKED_STATUSES

# ==============================================
# 🔒 LOCK ORDER
# ==============================================

async def check_order_editable(
    *,
    order: dict,
) -> None:
    """
    تتحقق من إمكانية تعديل الطلب
    
    Args:
        order: بيانات الطلب من قاعدة البيانات
        
    Raises:
        ValueError: إذا كان الطلب في حالة تمنع التعديل
    """
    status = str(
        order.get(
            "status",
            "",
        ),
    )
    
    if status in LOCKED_STATUSES:
        raise ValueError(
            f"order_locked_status_{status}",
        )
    
    return None
# ==============================================
# 📦 ORDERS SERVICE - HELPERS
# الدوال المساعدة (_check_order_editable)
# ==============================================

from typing import Any, Dict

from app.models.order import Order
from app.services.business.orders.constants import LOCKED_STATUSES

# ==============================================
# 🧩 TYPES
# ==============================================

OrderDict = Dict[str, Any]

# ==============================================
# 🔒 LOCK ORDER
# ==============================================

def check_order_editable(
    order: Order,
) -> None:
    """
    تتحقق من إمكانية تعديل الطلب.
    
    Args:
        order: كائن الطلب من SQLAlchemy
        
    Raises:
        ValueError: إذا كان الطلب في حالة تمنع التعديل
    """
    status = order.status

    if status in LOCKED_STATUSES:
        raise ValueError(
            f"order_locked_status_{status}",
        )

# ==============================================
# 🔒 CHECK ORDER EDITABLE (DICT VERSION)
# ==============================================

def check_order_editable_from_dict(
    order: OrderDict,
) -> None:
    """
    تتحقق من إمكانية تعديل الطلب (نسخة متوافقة مع الإصدار القديم).
    
    Args:
        order: بيانات الطلب من قاعدة البيانات (قاموس)
        
    Raises:
        ValueError: إذا كان الطلب في حالة تمنع التعديل
    """
    status = str(order.get("status", ""))

    if status in LOCKED_STATUSES:
        raise ValueError(
            f"order_locked_status_{status}",
        )

# ==============================================
# 🔒 CHECK ORDER EDITABLE BY STATUS
# ==============================================

def check_order_editable_by_status(
    status: str,
) -> None:
    """
    تتحقق من إمكانية تعديل الطلب بناءً على حالته.
    
    Args:
        status: حالة الطلب
        
    Raises:
        ValueError: إذا كانت الحالة تمنع التعديل
    """
    if status in LOCKED_STATUSES:
        raise ValueError(
            f"order_locked_status_{status}",
        )

# ==============================================
# ✅ IS ORDER EDITABLE
# ==============================================

def is_order_editable(
    status: str,
) -> bool:
    """
    تتحقق مما إذا كان الطلب قابلاً للتعديل.
    
    Args:
        status: حالة الطلب
        
    Returns:
        True إذا كان قابلاً للتعديل، False إذا كان مقفلاً
    """
    return status not in LOCKED_STATUSES
# ==============================================
# 📦 ORDERS SERVICE - ITEMS
# إدارة عناصر الطلب (add_item_to_order,
#  remove_item_from_order)
# ==============================================

from app.core.logger import logger

from app.repositories.orders_repo import (
    get_order,
)

from app.repositories.order_items_repo import (
    create_order_item,
    delete_order_item,
    get_order_items,
)

from app.repositories.order_item_options_repo import (
    create_order_item_option,
    delete_order_item_options,
)

from app.services.business.orders.helpers import check_order_editable

# ==============================================
# 🧩 TYPES
# ==============================================

OrderOptionPayload = dict[str, object]

# ==============================================
# ➕ ADD ITEM TO ORDER
# ==============================================

async def add_item_to_order(
    *,
    order_id: int,
    product_id: int,
    product_name: str,
    unit_price: float,
    quantity: int,
    total_price: float,
    options: list[OrderOptionPayload] | None = None,
) -> int:
    """
    إضافة عنصر إلى طلب موجود
    
    Args:
        order_id: معرف الطلب
        product_id: معرف المنتج
        product_name: اسم المنتج
        unit_price: سعر الوحدة
        quantity: الكمية
        total_price: السعر الإجمالي
        options: قائمة الخيارات (اختياري)
        
    Returns:
        int: معرف عنصر الطلب
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو كان مقفلاً
    """
    # جلب الطلب للتحقق
    order = await get_order(
        order_id=order_id,
    )
    
    if not order:
        raise ValueError(
            "order_not_found",
        )
    
    # التحقق من إمكانية التعديل
    await check_order_editable(
        order=order,
    )
    
    # التحقق من الكمية
    if quantity <= 0:
        raise ValueError(
            "invalid_quantity",
        )
    
    # إنشاء عنصر الطلب
    order_item_id = await create_order_item(
        order_id=order_id,
        product_id=product_id,
        product_name=product_name,
        unit_price=unit_price,
        quantity=quantity,
        total_price=total_price,
    )
    
    # إنشاء الخيارات إن وجدت
    if options:
        for option in options:
            await create_order_item_option(
                order_item_id=order_item_id,
                option_group_name=option["option_group_name"],
                option_name=option["option_name"],
                additional_price=option.get(
                    "additional_price",
                    0,
                ),
            )
    
    logger.info(
        "order_item_added",
        extra={
            "order_id": order_id,
            "order_item_id": order_item_id,
            "product_id": product_id,
            "quantity": quantity,
        },
    )
    
    return order_item_id

# ==============================================
# ❌ REMOVE ITEM FROM ORDER
# ==============================================

async def remove_item_from_order(
    *,
    order_id: int,
    order_item_id: int,
) -> None:
    """
    حذف عنصر من طلب
    
    Args:
        order_id: معرف الطلب
        order_item_id: معرف عنصر الطلب
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو كان مقفلاً
    """
    # جلب الطلب للتحقق
    order = await get_order(
        order_id=order_id,
    )
    
    if not order:
        raise ValueError(
            "order_not_found",
        )
    
    # التحقق من إمكانية التعديل
    await check_order_editable(
        order=order,
    )
    
    # حذف خيارات العنصر أولاً
    await delete_order_item_options(
        order_item_id=order_item_id,
    )
    
    # حذف عنصر الطلب
    await delete_order_item(
        order_item_id=order_item_id,
    )
    
    logger.info(
        "order_item_removed",
        extra={
            "order_id": order_id,
            "order_item_id": order_item_id,
        },
    )

# ==============================================
# 🔍 GET ORDER ITEMS
# ==============================================

async def get_order_items_list(
    *,
    order_id: int,
) -> list[dict]:
    """
    جلب جميع عناصر طلب معين
    
    Args:
        order_id: معرف الطلب
        
    Returns:
        list[dict]: قائمة عناصر الطلب
    """
    return await get_order_items(
        order_id=order_id,
    )
# ==============================================
# 📦 ORDERS SERVICE - ITEMS
# إدارة عناصر الطلب 
# (add_item_to_order, remove_item_from_order)
# ==============================================

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.order_item import OrderItem
from app.repositories.order_item_options_repo import (
    OrderItemOptionsRepository,
)
from app.repositories.order_items_repo import OrderItemsRepository
from app.repositories.orders_repo import OrdersRepository
from app.services.business.orders.helpers import check_order_editable

# ==============================================
# 🧩 TYPES
# ==============================================

OrderOptionPayload = Dict[str, Any]
OrderItemList = List[OrderItem]

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
    options: Optional[List[OrderOptionPayload]] = None,
    session: AsyncSession,
) -> OrderItem:
    """
    إضافة عنصر إلى طلب موجود.
    
    Args:
        order_id: معرف الطلب
        product_id: معرف المنتج
        product_name: اسم المنتج
        unit_price: سعر الوحدة
        quantity: الكمية
        total_price: السعر الإجمالي
        options: قائمة الخيارات (اختياري)
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        كائن OrderItem المنشأ
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو كان مقفلاً أو الكمية غير صالحة
    """
    logger.info(
        "add_item_to_order_started",
        extra={
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
        },
    )

    # جلب الطلب للتحقق
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "add_item_to_order_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # التحقق من إمكانية التعديل
    check_order_editable(order)

    # التحقق من الكمية
    if quantity <= 0:
        raise ValueError("invalid_quantity")

    # إنشاء عنصر الطلب
    items_repo = OrderItemsRepository(session=session)

    item_data: Dict[str, Any] = {
        "order_id": order_id,
        "product_id": product_id,
        "product_name": product_name,
        "unit_price": unit_price,
        "quantity": quantity,
        "total_price": total_price,
    }

    order_item = await items_repo.create(data=item_data)

    # إنشاء الخيارات إن وجدت
    if options:
        options_repo = OrderItemOptionsRepository(session=session)

        for option in options:
            option_data: Dict[str, Any] = {
                "order_item_id": order_item.id,
                "option_group_name": option["option_group_name"],
                "option_name": option["option_name"],
                "additional_price": option.get("additional_price", 0),
            }

            await options_repo.create(data=option_data)

    logger.info(
        "order_item_added_successfully",
        extra={
            "order_id": order_id,
            "order_item_id": order_item.id,
            "product_id": product_id,
            "quantity": quantity,
        },
    )

    return order_item


# ==============================================
# ❌ REMOVE ITEM FROM ORDER
# ==============================================

async def remove_item_from_order(
    *,
    order_id: int,
    order_item_id: int,
    session: AsyncSession,
) -> None:
    """
    حذف عنصر من طلب.
    
    Args:
        order_id: معرف الطلب
        order_item_id: معرف عنصر الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو كان مقفلاً
    """
    logger.info(
        "remove_item_from_order_started",
        extra={
            "order_id": order_id,
            "order_item_id": order_item_id,
        },
    )

    # جلب الطلب للتحقق
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "remove_item_from_order_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # التحقق من إمكانية التعديل
    check_order_editable(order)

    # حذف خيارات العنصر أولاً
    options_repo = OrderItemOptionsRepository(session=session)
    await options_repo.delete_by_order_item(order_item_id=order_item_id)

    # حذف عنصر الطلب
    items_repo = OrderItemsRepository(session=session)
    await items_repo.delete(id=order_item_id)

    logger.info(
        "order_item_removed_successfully",
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
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> OrderItemList:
    """
    جلب جميع عناصر طلب معين.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        
    Returns:
        قائمة عناصر الطلب
    """
    logger.info(
        "get_order_items_list_started",
        extra={
            "order_id": order_id,
            "skip": skip,
            "limit": limit,
        },
    )

    items_repo = OrderItemsRepository(session=session)
    items = await items_repo.get_by_order_id(
        order_id=order_id,
        skip=skip,
        limit=limit,
    )

    logger.info(
        "order_items_list_retrieved",
        extra={
            "order_id": order_id,
            "count": len(items),
        },
    )

    return items


# ==============================================
# 🔍 GET ORDER ITEM BY ID
# ==============================================

async def get_order_item_by_id(
    *,
    order_item_id: int,
    session: AsyncSession,
) -> Optional[OrderItem]:
    """
    جلب عنصر طلب بالمعرف.
    
    Args:
        order_item_id: معرف عنصر الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        كائن OrderItem أو None
    """
    logger.info(
        "get_order_item_by_id_started",
        extra={"order_item_id": order_item_id},
    )

    items_repo = OrderItemsRepository(session=session)
    item = await items_repo.get_by_id(id=order_item_id)

    return item


# ==============================================
# 🔢 COUNT ORDER ITEMS
# ==============================================

async def count_order_items(
    *,
    order_id: int,
    session: AsyncSession,
) -> int:
    """
    حساب عدد عناصر طلب معين.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        عدد العناصر
    """
    logger.info(
        "count_order_items_started",
        extra={"order_id": order_id},
    )

    items_repo = OrderItemsRepository(session=session)
    count = await items_repo.count_by_order(order_id=order_id)

    return count


# ==============================================
# 💰 GET ORDER ITEMS SUBTOTAL
# ==============================================

async def get_order_items_subtotal(
    *,
    order_id: int,
    session: AsyncSession,
) -> float:
    """
    حساب المجموع الفرعي لعناصر طلب معين.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        المجموع الفرعي
    """
    logger.info(
        "get_order_items_subtotal_started",
        extra={"order_id": order_id},
    )

    items_repo = OrderItemsRepository(session=session)
    subtotal = await items_repo.get_subtotal(order_id=order_id)

    return subtotal
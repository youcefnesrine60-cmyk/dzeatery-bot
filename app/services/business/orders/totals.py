# ==============================================
# 📦 ORDERS SERVICE - TOTALS
# حساب الإجماليات (calculate_order_totals)
# ==============================================

from app.core.logger import logger

from app.repositories.orders_repo import (
    get_order,
    update_order_totals,
)

from app.repositories.order_items_repo import (
    get_order_items,
)

from app.services.business.orders.helpers import check_order_editable

# ==============================================
# 🧮 CALCULATE ORDER TOTALS
# ==============================================

async def calculate_order_totals(
    *,
    order_id: int,
) -> tuple[float, float, float, float, float]:
    """
    حساب إجماليات الطلب من عناصره
    
    Args:
        order_id: معرف الطلب
        
    Returns:
        tuple: (subtotal, discount, tax, delivery, total)
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب
    """
    # جلب الطلب
    order = await get_order(
        order_id=order_id,
    )
    
    if not order:
        raise ValueError(
            "order_not_found",
        )
    
    # جلب عناصر الطلب
    items = await get_order_items(
        order_id=order_id,
    )
    
    # حساب المجموع الفرعي من العناصر
    subtotal = 0.0
    
    for item in items:
        subtotal += float(
            item.get(
                "total_price",
                0,
            ),
        )
    
    # جلب الخصم والضريبة والتوصيل من الطلب
    discount = float(
        order.get(
            "discount_amount",
            0,
        ),
    )
    
    tax = float(
        order.get(
            "tax_amount",
            0,
        ),
    )
    
    delivery = float(
        order.get(
            "delivery_amount",
            0,
        ),
    )
    
    # حساب المجموع الكلي
    total = subtotal - discount + tax + delivery
    
    # تحديث إجماليات الطلب
    await update_order_totals(
        order_id=order_id,
        subtotal_amount=subtotal,
        discount_amount=discount,
        tax_amount=tax,
        delivery_amount=delivery,
        total_amount=total,
    )
    
    logger.info(
        "order_totals_calculated",
        extra={
            "order_id": order_id,
            "subtotal": subtotal,
            "total": total,
        },
    )
    
    return (subtotal, discount, tax, delivery, total)

# ==============================================
# 💰 UPDATE ORDER TOTALS
# ==============================================

async def update_order_totals(
    *,
    order_id: int,
    subtotal_amount: float,
    discount_amount: float,
    tax_amount: float,
    delivery_amount: float,
    total_amount: float,
) -> None:
    """
    تحديث إجماليات الطلب
    
    Args:
        order_id: معرف الطلب
        subtotal_amount: المجموع الفرعي
        discount_amount: مبلغ الخصم
        tax_amount: مبلغ الضريبة
        delivery_amount: مبلغ التوصيل
        total_amount: المجموع الكلي
        
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

    await update_order_totals(
        order_id=order_id,
        subtotal_amount=subtotal_amount,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        delivery_amount=delivery_amount,
        total_amount=total_amount,
    )

    logger.info(
        "order_totals_updated",
        extra={
            "order_id": order_id,
        },
    )
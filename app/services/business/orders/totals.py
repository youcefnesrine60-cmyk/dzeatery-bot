# ==============================================
# 📦 ORDERS SERVICE - TOTALS
# حساب الإجماليات 
# (calculate_order_totals, update_order_totals)
# ==============================================

from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.order import Order
from app.repositories.order_items_repo import OrderItemsRepository
from app.repositories.orders_repo import OrdersRepository
from app.services.business.orders.helpers import check_order_editable

# ==============================================
# 🧩 TYPES
# ==============================================

OrderTotals = Tuple[float, float, float, float, float]

# ==============================================
# 🧮 CALCULATE ORDER TOTALS
# ==============================================

async def calculate_order_totals(
    *,
    order_id: int,
    session: AsyncSession,
) -> OrderTotals:
    """
    حساب إجماليات الطلب من عناصره.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        (subtotal, discount, tax, delivery, total)
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "calculate_order_totals_started",
        extra={"order_id": order_id},
    )

    # جلب الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "calculate_order_totals_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # جلب عناصر الطلب
    items_repo = OrderItemsRepository(session=session)
    items = await items_repo.get_by_order_id(order_id=order_id)

    # حساب المجموع الفرعي من العناصر
    subtotal = sum(float(item.total_price) for item in items)

    # جلب الخصم والضريبة والتوصيل من الطلب
    discount = float(order.discount_amount or 0)
    tax = float(order.tax_amount or 0)
    delivery = float(order.delivery_amount or 0)

    # حساب المجموع الكلي
    total = subtotal - discount + tax + delivery

    # تحديث إجماليات الطلب
    await orders_repo.update_totals(
        order_id=order_id,
        subtotal_amount=subtotal,
        discount_amount=discount,
        tax_amount=tax,
        delivery_amount=delivery,
        total_amount=total,
    )

    logger.info(
        "order_totals_calculated_successfully",
        extra={
            "order_id": order_id,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "delivery": delivery,
            "total": total,
            "items_count": len(items),
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
    session: AsyncSession,
) -> Order:
    """
    تحديث إجماليات الطلب.
    
    Args:
        order_id: معرف الطلب
        subtotal_amount: المجموع الفرعي
        discount_amount: مبلغ الخصم
        tax_amount: مبلغ الضريبة
        delivery_amount: مبلغ التوصيل
        total_amount: المجموع الكلي
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        الطلب المُحدّث
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب أو كان مقفلاً
    """
    logger.info(
        "update_order_totals_started",
        extra={
            "order_id": order_id,
            "subtotal_amount": subtotal_amount,
            "total_amount": total_amount,
        },
    )

    # جلب الطلب
    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "update_order_totals_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    # التحقق من إمكانية التعديل
    check_order_editable(order)

    # تحديث الإجماليات
    updated_order = await orders_repo.update_totals(
        order_id=order_id,
        subtotal_amount=subtotal_amount,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        delivery_amount=delivery_amount,
        total_amount=total_amount,
    )

    if not updated_order:
        logger.error(
            "update_order_totals_update_failed",
            extra={"order_id": order_id},
        )
        raise ValueError("order_update_failed")

    logger.info(
        "order_totals_updated_successfully",
        extra={
            "order_id": order_id,
            "subtotal_amount": subtotal_amount,
            "total_amount": total_amount,
        },
    )

    return updated_order


# ==============================================
# 🔄 RECALCULATE ORDER TOTALS
# ==============================================

async def recalculate_order_totals(
    *,
    order_id: int,
    session: AsyncSession,
) -> OrderTotals:
    """
    إعادة حساب إجماليات الطلب (جمع بين calculate و update).
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        (subtotal, discount, tax, delivery, total)
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "recalculate_order_totals_started",
        extra={"order_id": order_id},
    )

    # حساب الإجماليات
    totals = await calculate_order_totals(
        order_id=order_id,
        session=session,
    )

    # تحديث الإجماليات في قاعدة البيانات (يتم داخل calculate_order_totals)

    logger.info(
        "recalculate_order_totals_completed",
        extra={
            "order_id": order_id,
            "subtotal": totals[0],
            "total": totals[4],
        },
    )

    return totals


# ==============================================
# 📊 GET ORDER TOTALS
# ==============================================

async def get_order_totals(
    *,
    order_id: int,
    session: AsyncSession,
) -> OrderTotals:
    """
    الحصول على إجماليات الطلب دون إعادة الحساب.
    
    Args:
        order_id: معرف الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        (subtotal, discount, tax, delivery, total)
        
    Raises:
        ValueError: إذا لم يتم العثور على الطلب
    """
    logger.info(
        "get_order_totals_started",
        extra={"order_id": order_id},
    )

    orders_repo = OrdersRepository(session=session)
    order = await orders_repo.get_by_id(id=order_id)

    if not order:
        logger.error(
            "get_order_totals_order_not_found",
            extra={"order_id": order_id},
        )
        raise ValueError("order_not_found")

    totals = (
        float(order.subtotal_amount or 0),
        float(order.discount_amount or 0),
        float(order.tax_amount or 0),
        float(order.delivery_amount or 0),
        float(order.total_amount or 0),
    )

    logger.info(
        "get_order_totals_retrieved",
        extra={
            "order_id": order_id,
            "subtotal": totals[0],
            "total": totals[4],
        },
    )

    return totals
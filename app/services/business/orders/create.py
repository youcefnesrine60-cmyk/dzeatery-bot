# ==============================================
# 📦 ORDERS SERVICE - CREATE
# إنشاء الطلب (create_restaurant_order, 
# create_order_with_items_tx)
# ==============================================

from psycopg import AsyncConnection

from app.core.logger import logger

from app.repositories.orders_repo import (
    create_order,
    create_order_tx,
)

from app.repositories.order_status_history_repo import (
    create_status_history,
    create_status_history_tx,
)

from app.repositories.order_items_repo import (
    create_order_item_tx,
)

from app.repositories.order_item_options_repo import (
    create_order_item_option_tx,
)

from app.repositories.restaurant_order_counters_repo import (
    generate_next_order_number_tx,
)

from app.repositories.restaurant_metrics_repo import (
    register_order_metrics_tx,
)

from app.services.business.feature_usage_counter_engine import (
    increase_usage,
    increase_usage_tx,
)

from app.services.business.restaurant_metrics_service import (
    order_registered,
)

from app.services.business.orders.constants import ORDERS_FEATURE_ID

# ==============================================
# 🧩 TYPES
# ==============================================

OrderItemPayload = dict[str, object]

# ==============================================
# ➕ CREATE ORDER
# ==============================================

async def create_restaurant_order(
    *,
    restaurant_id: int,
    branch_id: int | None,
    table_id: int | None,
    employee_id: int | None,
    order_number: str,
    order_type: str,
    customer_name: str | None,
    customer_phone: str | None,
    delivery_address: str | None,
    customer_note: str | None,
    subtotal_amount: float = 0,
    discount_amount: float = 0,
    tax_amount: float = 0,
    delivery_amount: float = 0,
    total_amount: float = 0,
) -> int:
    """
    إنشاء طلب جديد
    
    Args:
        restaurant_id: معرف المطعم
        branch_id: معرف الفرع (اختياري)
        table_id: معرف الطاولة (اختياري)
        employee_id: معرف الموظف (اختياري)
        order_number: رقم الطلب
        order_type: نوع الطلب (dine_in, delivery)
        customer_name: اسم العميل (اختياري)
        customer_phone: هاتف العميل (اختياري)
        delivery_address: عنوان التوصيل (اختياري)
        customer_note: ملاحظة العميل (اختياري)
        subtotal_amount: المجموع الفرعي
        discount_amount: مبلغ الخصم
        tax_amount: مبلغ الضريبة
        delivery_amount: مبلغ التوصيل
        total_amount: المجموع الكلي
        
    Returns:
        int: معرف الطلب الجديد
    """
    order_id = await create_order(
        restaurant_id=restaurant_id,
        branch_id=branch_id,
        table_id=table_id,
        employee_id=employee_id,
        order_number=order_number,
        order_type=order_type,
        customer_name=customer_name,
        customer_phone=customer_phone,
        delivery_address=delivery_address,
        customer_note=customer_note,
        status="received",
        subtotal_amount=subtotal_amount,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        delivery_amount=delivery_amount,
        total_amount=total_amount,
    )

    await create_status_history(
        order_id=order_id,
        old_status=None,
        new_status="received",
        changed_by_employee_id=employee_id,
        note="order_created",
    )

    await increase_usage(
        restaurant_id=restaurant_id,
        feature_id=ORDERS_FEATURE_ID,
    )

    await order_registered(
        restaurant_id=restaurant_id,
        order_total=total_amount,
    )

    logger.info(
        "restaurant_order_created",
        extra={
            "order_id": order_id,
            "restaurant_id": restaurant_id,
        },
    )

    return order_id

# ==============================================
# 🚀 CREATE ORDER WITH ITEMS TX
# ==============================================

async def create_order_with_items_tx(
    *,
    conn: AsyncConnection,
    restaurant_id: int,
    branch_id: int | None,
    table_id: int | None,
    employee_id: int | None,
    order_type: str,
    customer_name: str | None,
    customer_phone: str | None,
    delivery_address: str | None,
    customer_note: str | None,
    subtotal_amount: float,
    discount_amount: float,
    tax_amount: float,
    delivery_amount: float,
    total_amount: float,
    items: list[OrderItemPayload],
) -> int:
    """
    إنشاء طلب مع عناصره في معاملة واحدة
    
    Args:
        conn: اتصال قاعدة البيانات
        restaurant_id: معرف المطعم
        branch_id: معرف الفرع (اختياري)
        table_id: معرف الطاولة (اختياري)
        employee_id: معرف الموظف (اختياري)
        order_type: نوع الطلب
        customer_name: اسم العميل (اختياري)
        customer_phone: هاتف العميل (اختياري)
        delivery_address: عنوان التوصيل (اختياري)
        customer_note: ملاحظة العميل (اختياري)
        subtotal_amount: المجموع الفرعي
        discount_amount: مبلغ الخصم
        tax_amount: مبلغ الضريبة
        delivery_amount: مبلغ التوصيل
        total_amount: المجموع الكلي
        items: قائمة عناصر الطلب
        
    Returns:
        int: معرف الطلب الجديد
    """
    # ==========================================
    # Generate Order Number
    # ==========================================

    order_number = await generate_next_order_number_tx(
        conn=conn,
        restaurant_id=restaurant_id,
    )

    # ==========================================
    # Create Order
    # ==========================================

    order_id = await create_order_tx(
        conn=conn,
        restaurant_id=restaurant_id,
        branch_id=branch_id,
        table_id=table_id,
        employee_id=employee_id,
        order_number=order_number,
        order_type=order_type,
        customer_name=customer_name,
        customer_phone=customer_phone,
        delivery_address=delivery_address,
        customer_note=customer_note,
        status="received",
        subtotal_amount=subtotal_amount,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        delivery_amount=delivery_amount,
        total_amount=total_amount,
    )

    # ==========================================
    # Create Order Items
    # ==========================================

    for item in items:
        order_item_id = await create_order_item_tx(
            conn=conn,
            order_id=order_id,
            product_id=item["product_id"],
            product_name=item["product_name"],
            unit_price=item["unit_price"],
            quantity=item["quantity"],
            total_price=item["total_price"],
        )

        options = item.get(
            "options",
            [],
        )

        for option in options:
            await create_order_item_option_tx(
                conn=conn,
                order_item_id=order_item_id,
                option_group_name=option["option_group_name"],
                option_name=option["option_name"],
                additional_price=option.get(
                    "additional_price",
                    0,
                ),
            )

    # ==========================================
    # Create Initial Status
    # ==========================================

    await create_status_history_tx(
        conn=conn,
        order_id=order_id,
        old_status=None,
        new_status="received",
        changed_by_employee_id=employee_id,
        note="Order Created",
    )

    # ==========================================
    # Update Metrics
    # ==========================================

    await register_order_metrics_tx(
        conn=conn,
        restaurant_id=restaurant_id,
        order_total=total_amount,
    )

    # ==========================================
    # Increase Orders Feature Usage
    # ==========================================

    await increase_usage_tx(
        conn=conn,
        restaurant_id=restaurant_id,
        feature_id=ORDERS_FEATURE_ID,
        amount=1,
    )

    return order_id
# ==============================================
# 📦 ORDER ITEMS SERVICE
# Business Logic Layer
# ==============================================

from app.core.logger import logger

from app.repositories.order_items_repo import (
    create_order_item,
    delete_order_item,
    delete_order_items,
    get_order_item,
    get_order_items,
    count_order_items,
    get_order_items_subtotal,
    update_order_item_quantity,
)

# ==============================================
# ➕ CREATE ORDER ITEM
# ==============================================

async def add_order_item(
    *,
    order_id: int,
    product_id: int,
    product_name: str,
    unit_price: float,
    quantity: int,
) -> int:

    if quantity <= 0:
        raise ValueError(
            "invalid_quantity"
        )

    if unit_price < 0:
        raise ValueError(
            "invalid_unit_price"
        )

    total_price = (
        unit_price * quantity
    )

    order_item_id = await create_order_item(
        order_id=order_id,
        product_id=product_id,
        product_name=product_name,
        unit_price=unit_price,
        quantity=quantity,
        total_price=total_price,
    )

    logger.info(
        "order_item_added",
        extra={
            "order_item_id": order_item_id,
            "order_id": order_id,
        },
    )

    return order_item_id

# ==============================================
# 🔍 GET ORDER ITEM
# ==============================================

async def get_item(
    *,
    order_item_id: int,
):

    return await get_order_item(
        order_item_id=order_item_id,
    )

# ==============================================
# 🔍 GET ORDER ITEMS
# ==============================================

async def list_order_items(
    *,
    order_id: int,
):

    return await get_order_items(
        order_id=order_id,
    )

# ==============================================
# 🔢 COUNT ITEMS
# ==============================================

async def get_items_count(
    *,
    order_id: int,
) -> int:

    return await count_order_items(
        order_id=order_id,
    )

# ==============================================
# 💰 GET SUBTOTAL
# ==============================================

async def get_subtotal(
    *,
    order_id: int,
) -> float:

    return await get_order_items_subtotal(
        order_id=order_id,
    )

# ==============================================
# ✏️ CHANGE QUANTITY
# ==============================================

async def change_item_quantity(
    *,
    order_item_id: int,
    quantity: int,
) -> None:

    item = await get_order_item(
        order_item_id=order_item_id,
    )

    if not item:
        raise ValueError(
            "order_item_not_found"
        )

    if quantity <= 0:
        raise ValueError(
            "invalid_quantity"
        )

    unit_price = float(
        item["unit_price"]
    )

    total_price = (
        unit_price * quantity
    )

    await update_order_item_quantity(
        order_item_id=order_item_id,
        quantity=quantity,
        total_price=total_price,
    )

    logger.info(
        "order_item_quantity_changed",
        extra={
            "order_item_id": order_item_id,
            "quantity": quantity,
        },
    )

# ==============================================
# ❌ DELETE ITEM
# ==============================================

async def remove_order_item(
    *,
    order_item_id: int,
) -> None:

    item = await get_order_item(
        order_item_id=order_item_id,
    )

    if not item:
        raise ValueError(
            "order_item_not_found"
        )

    await delete_order_item(
        order_item_id=order_item_id,
    )

    logger.info(
        "order_item_removed",
        extra={
            "order_item_id": order_item_id,
        },
    )

# ==============================================
# ❌ DELETE ALL ITEMS
# ==============================================

async def remove_all_order_items(
    *,
    order_id: int,
) -> None:

    await delete_order_items(
        order_id=order_id,
    )

    logger.info(
        "all_order_items_removed",
        extra={
            "order_id": order_id,
        },
    )
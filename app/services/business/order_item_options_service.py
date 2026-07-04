# ==============================================
# 🎛 ORDER ITEM OPTIONS SERVICE
# Business Logic Layer
# ==============================================

from app.core.logger import logger

from app.repositories.order_item_options_repo import (
    create_order_item_option,
    get_order_item_option,
    get_order_item_options,
    get_order_item_options_total,
    count_order_item_options,
    delete_order_item_option,
    delete_order_item_options,
)

# ==============================================
# ➕ ADD OPTION
# ==============================================

async def add_order_item_option(
    *,
    order_item_id: int,
    option_group_name: str,
    option_name: str,
    additional_price: float = 0,
) -> int:

    if not option_group_name.strip():
        raise ValueError(
            "option_group_name_required"
        )

    if not option_name.strip():
        raise ValueError(
            "option_name_required"
        )

    if additional_price < 0:
        raise ValueError(
            "invalid_additional_price"
        )

    option_id = await create_order_item_option(
        order_item_id=order_item_id,
        option_group_name=option_group_name,
        option_name=option_name,
        additional_price=additional_price,
    )

    logger.info(
        "order_item_option_added",
        extra={
            "option_id": option_id,
            "order_item_id": order_item_id,
        },
    )

    return option_id

# ==============================================
# 🔍 GET OPTION
# ==============================================

async def get_option(
    *,
    option_id: int,
):

    return await get_order_item_option(
        option_id=option_id,
    )

# ==============================================
# 🔍 GET ITEM OPTIONS
# ==============================================

async def list_item_options(
    *,
    order_item_id: int,
):

    return await get_order_item_options(
        order_item_id=order_item_id,
    )

# ==============================================
# 💰 GET OPTIONS TOTAL
# ==============================================

async def get_options_total(
    *,
    order_item_id: int,
) -> float:

    return await get_order_item_options_total(
        order_item_id=order_item_id,
    )

# ==============================================
# 🔢 COUNT OPTIONS
# ==============================================

async def get_options_count(
    *,
    order_item_id: int,
) -> int:

    return await count_order_item_options(
        order_item_id=order_item_id,
    )

# ==============================================
# ❌ REMOVE OPTION
# ==============================================

async def remove_option(
    *,
    option_id: int,
) -> None:

    option = await get_order_item_option(
        option_id=option_id,
    )

    if not option:
        raise ValueError(
            "order_item_option_not_found"
        )

    await delete_order_item_option(
        option_id=option_id,
    )

    logger.info(
        "order_item_option_removed",
        extra={
            "option_id": option_id,
        },
    )

# ==============================================
# ❌ REMOVE ALL OPTIONS
# ==============================================

async def remove_all_item_options(
    *,
    order_item_id: int,
) -> None:

    await delete_order_item_options(
        order_item_id=order_item_id,
    )

    logger.info(
        "all_order_item_options_removed",
        extra={
            "order_item_id": order_item_id,
        },
    )
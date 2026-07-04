# ==============================================
# 🏢 BRANCH SERVICE
# Business Logic Layer
# ==============================================

from app.guards.feature_guard import (
    require_feature,
)

from app.repositories.branches_repo import (
    create_branch,
    get_branch,
    update_branch,
    deactivate_branch,
    get_restaurant_branches,
    count_restaurant_branches,
)

from app.repositories.branch_pricing_repo import (
    calculate_branch_cost,
)

from app.services.business.feature_usage_counter_engine import (
    increase_usage,
    decrease_usage,
)

from app.core.logger import logger

# ==============================================
# 🧩 FEATURE IDS
# ==============================================

BRANCH_FEATURE_ID = 3

# ==============================================
# ➕ CREATE BRANCH
# ==============================================

async def create_restaurant_branch(
    *,
    restaurant_id: int,
    name: str,
    phone: str | None,
    wilaya: str | None,
    lat: float | None,
    lng: float | None,
) -> int:

    await require_feature(
        restaurant_id=restaurant_id,
        feature_id=BRANCH_FEATURE_ID,
    )

    branch_id = await create_branch(
        restaurant_id=restaurant_id,
        name=name,
        phone=phone,
        wilaya=wilaya,
        lat=lat,
        lng=lng,
    )

    await increase_usage(
        restaurant_id=restaurant_id,
        feature_id=BRANCH_FEATURE_ID,
    )

    logger.info(
        "restaurant_branch_created",
        extra={
            "branch_id": branch_id,
            "restaurant_id": restaurant_id,
        },
    )

    return branch_id


# ==============================================
# ✏️ UPDATE BRANCH
# ==============================================

async def update_restaurant_branch(
    *,
    branch_id: int,
    name: str,
    phone: str | None,
    wilaya: str | None,
    lat: float | None,
    lng: float | None,
) -> None:

    await update_branch(
        branch_id=branch_id,
        name=name,
        phone=phone,
        wilaya=wilaya,
        lat=lat,
        lng=lng,
    )

    logger.info(
        "restaurant_branch_updated",
        extra={
            "branch_id": branch_id,
        },
    )


# ==============================================
# ❌ REMOVE BRANCH
# ==============================================

async def remove_restaurant_branch(
    *,
    branch_id: int,
) -> None:

    branch = await get_branch(
        branch_id=branch_id,
    )

    if not branch:
        raise ValueError(
            "branch_not_found"
        )

    await deactivate_branch(
        branch_id=branch_id,
    )

    await decrease_usage(
        restaurant_id=branch["restaurant_id"],
        feature_id=BRANCH_FEATURE_ID,
    )

    logger.info(
        "restaurant_branch_removed",
        extra={
            "branch_id": branch_id,
            "restaurant_id": branch["restaurant_id"],
        },
    )


# ==============================================
# 📋 LIST BRANCHES
# ==============================================

async def list_restaurant_branches(
    *,
    restaurant_id: int,
):

    return await get_restaurant_branches(
        restaurant_id=restaurant_id,
    )


# ==============================================
# 🔢 COUNT BRANCHES
# ==============================================

async def get_branches_count(
    *,
    restaurant_id: int,
) -> int:

    return await count_restaurant_branches(
        restaurant_id=restaurant_id,
    )


# ==============================================
# 💰 BRANCH COST
# ==============================================

async def get_branch_cost(
    *,
    restaurant_id: int,
) -> float:

    branches_count = await get_branches_count(
        restaurant_id=restaurant_id,
    )

    return await calculate_branch_cost(
        branches_count=branches_count,
    )
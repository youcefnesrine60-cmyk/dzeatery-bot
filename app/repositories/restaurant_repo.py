# ==============================================
# 🍽️ RESTAURANT REPOSITORY
# Async Psycopg3 Version
# ==============================================

from app.core.db import (
    fetch, 
    fetchrow, 
    insert_returning_id
)

from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

Restaurant = dict[str, str | int | float | None]

# ==============================================
# ➕ CREATE RESTAURANT
# ==============================================

async def create_restaurant(
    *,
    owner_id: int,
    name: str,
    restaurant_type: str,
    phone: str,
    wilaya: str,
    lat: float,
    lng: float,
) -> int:

    restaurant_id = await insert_returning_id(
        """
        INSERT INTO restaurants (
            owner_id,
            name,
            type,
            phone,
            wilaya,
            lat,
            lng
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        owner_id,
        name,
        restaurant_type,
        phone,
        wilaya,
        lat,
        lng,
    )

    logger.info(
        "restaurant_created",
        extra={
            "restaurant_id": restaurant_id,
            "owner_id": owner_id,
            "restaurant_name": name,
        },
    )

    return restaurant_id


# ==============================================
# 🔍 BASE SELECT
# ==============================================

_RESTAURANT_SELECT = """
SELECT
    id,
    owner_id,
    name,
    type,
    phone,
    wilaya,
    lat,
    lng
FROM restaurants
"""


def _row_to_dict(row) -> Restaurant:
    return {
        "id": row["id"],
        "owner_id": row["owner_id"],
        "name": row["name"],
        "type": row["type"],
        "phone": row["phone"],
        "wilaya": row["wilaya"],
        "lat": row["lat"],
        "lng": row["lng"],
    }


# ==============================================
# 🔍 RESTAURANT EXISTS FOR OWNER
# ==============================================

async def restaurant_exists_for_owner(
    *,
    owner_id: int,
    name: str,
    phone: str,
    wilaya: str,
    lat: float,
    lng: float,
) -> bool:

    row = await fetchrow(
        """
        SELECT 1
        FROM restaurants
        WHERE owner_id = %s
          AND LOWER(name) = LOWER(%s)
          AND phone = %s
          AND LOWER(wilaya) = LOWER(%s)
          AND lat = %s
          AND lng = %s
        LIMIT 1
        """,
        owner_id,
        name,
        phone,
        wilaya,
        lat,
        lng,
    )

    exists = row is not None

    logger.info(
        "restaurant_exists_checked",
        extra={
            "owner_id": owner_id,
            "restaurant_name": name,
            "exists": exists,
        },
    )

    return exists


# ==============================================
# 🔍 GET RESTAURANT BY ID
# ==============================================

async def get_restaurant_by_id(
    *,
    restaurant_id: int,
) -> Restaurant | None:

    row = await fetchrow(
        _RESTAURANT_SELECT + " WHERE id = %s",
        restaurant_id,
    )

    if not row:
        logger.warning(
            "restaurant_not_found",
            extra={"restaurant_id": restaurant_id},
        )
        return None

    logger.info(
        "restaurant_found",
        extra={
            "restaurant_id": restaurant_id,
            "owner_id": row["owner_id"],
        },
    )

    return _row_to_dict(row)


# ==============================================
# 🔍 GET OWNER RESTAURANTS
# ==============================================

async def get_restaurants_by_owner(
    *,
    owner_id: int,
) -> list[Restaurant]:
    
    """
    جلب جميع مطاعم مالك معين
    
    Args:
        owner_id: معرف المالك
        
    Returns:
        list[Restaurant]: قائمة المطاعم
    """

    rows = await fetch(
        _RESTAURANT_SELECT + """
        WHERE owner_id = %s
        ORDER BY id DESC
        """,
        owner_id,
    )

    restaurants = [_row_to_dict(row) for row in rows]

    logger.info(
        "owner_restaurants_fetched",
        extra={
            "owner_id": owner_id,
            "count": len(restaurants),
        },
    )

    return restaurants


# ==============================================
# 📥 GET ALL RESTAURANTS
# ==============================================

async def get_all_restaurants() -> list[Restaurant]:

    rows = await fetch(
        _RESTAURANT_SELECT + """
        ORDER BY id DESC
        """
    )

    restaurants = [_row_to_dict(row) for row in rows]

    logger.info(
        "restaurants_fetched",
        extra={"count": len(restaurants)},
    )

    return restaurants
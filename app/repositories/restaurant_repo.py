# ==============================================
# 🍽️ RESTAURANT REPOSITORY
# ==============================================

from app.core.db import (
    get_cursor
)

from app.core.logger import (
    logger
)

# ==============================================
# 📥 GET ALL RESTAURANTS
# ==============================================

def get_all_restaurants() -> list[dict]:

    cur = get_cursor()

    cur.execute("""
        SELECT
            id,
            name,
            owner,
            type,
            phone,
            wilaya,
            lat,
            lng,
            chat_id
        FROM restaurants
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    logger.info(

        "restaurants_fetched",

        extra={
            "count": len(rows)
        }
    )

    restaurants = []

    for row in rows:

        restaurants.append({

            "id": row[0],
            "restaurant": row[1],
            "owner": row[2],
            "type": row[3],
            "phone": row[4],
            "wilaya": row[5],
            "lat": row[6],
            "lng": row[7],
            "chat_id": row[8]
        })

    return restaurants

# ==============================================
# 🔍 CHECK RESTAURANT EXISTS
# ==============================================

def restaurant_exists(

    *,

    name: str

) -> bool:

    cur = get_cursor()

    cur.execute("""
        SELECT 1
        FROM restaurants
        WHERE LOWER(name) = LOWER(%s)
    """, (name,))

    result = cur.fetchone()

    exists = result is not None

    logger.info(

        "restaurant_exists_checked",

        extra={
            "restaurant": name,
            "exists": exists
        }
    )

    return exists

# ==============================================
# 💾 SAVE RESTAURANT
# ==============================================

def save_restaurant(

    *,

    data: dict

) -> None:

    cur = get_cursor()

    cur.execute("""
        INSERT INTO restaurants
        (
            name,
            owner,
            type,
            phone,
            wilaya,
            lat,
            lng,
            chat_id
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data["restaurant"],
        data["owner"],
        data["type"],
        data["phone"],
        data["wilaya"],
        data["lat"],
        data["lng"],
        data["chat_id"]
    ))

    logger.info(

        "restaurant_saved",

        extra={

            "chat_id": data["chat_id"],

            "restaurant": data["restaurant"]
        }
    )

# ==============================================
# 🔍 GET RESTAURANT BY ID
# ==============================================

def get_restaurant_by_id(

    *,

    restaurant_id: int

) -> dict | None:

    cur = get_cursor()

    cur.execute("""
        SELECT
            id,
            name,
            owner,
            type,
            phone,
            wilaya,
            lat,
            lng,
            chat_id
        FROM restaurants
        WHERE id = %s
    """, (restaurant_id,))

    row = cur.fetchone()

    # ==========================================
    # 🚫 NOT FOUND
    # ==========================================

    if not row:

        logger.warning(

            "restaurant_not_found",

            extra={
                "restaurant_id": restaurant_id
            }
        )

        return None

    # ==========================================
    # ✅ FOUND
    # ==========================================

    logger.info(

        "restaurant_found",

        extra={
            "restaurant_id": restaurant_id
        }
    )

    return {

        "id": row[0],
        "restaurant": row[1],
        "owner": row[2],
        "type": row[3],
        "phone": row[4],
        "wilaya": row[5],
        "lat": row[6],
        "lng": row[7],
        "chat_id": row[8]
    }
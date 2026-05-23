# ==============================================
# 🍽️ RESTAURANT REPOSITORY
# ==============================================

from app.core.db import (
    get_cursor,
    commit,
    rollback
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

        "Fetched all restaurants",

        extra={
            "count": len(rows)
        }
    )

    restaurants = []

    for row in rows:

        restaurants.append({

            "id": row[0],
            "name": row[1],
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

def exists(name: str) -> bool:

    cur = get_cursor()

    cur.execute("""
        SELECT 1
        FROM restaurants
        WHERE LOWER(name)=LOWER(%s)
    """, (name,))

    result = cur.fetchone()

    logger.info(

        "Checked restaurant existence",

        extra={
            "name": name,
            "exists": result is not None
        }
    )

    return result is not None


# ==============================================
# 💾 SAVE RESTAURANT
# ==============================================

def save(data: dict) -> None:

    cur = get_cursor()

    try:

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
            data["name"],
            data["owner"],
            data["type"],
            data["phone"],
            data["wilaya"],
            data["lat"],
            data["lng"],
            data["chat_id"]
        ))

        # ======================================
        # 💾 SAVE CHANGES
        # ======================================

        commit()

        logger.info(

            "Restaurant saved successfully",

            extra={
                "restaurant": data["name"],
                "chat_id": data["chat_id"]
            }
        )

    except Exception as e:

        # ======================================
        # 🔄 ROLLBACK ON FAILURE
        # ======================================

        rollback()

        logger.error(

            "restaurant_save_failed",

            extra={
                "error": str(e),
                "restaurant": data.get("name")
            }
        )

        raise


# ==============================================
# 🔍 GET RESTAURANT BY ID
# ==============================================

def get_restaurant_by_id(

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
        WHERE id=%s
    """, (restaurant_id,))

    row = cur.fetchone()

    # ==========================================
    # 🚫 NOT FOUND
    # ==========================================

    if not row:

        logger.warning(

            "Restaurant not found",

            extra={
                "restaurant_id": restaurant_id
            }
        )

        return None

    # ==========================================
    # ✅ FOUND
    # ==========================================

    logger.info(

        "Restaurant found",

        extra={
            "restaurant_id": restaurant_id
        }
    )

    return {

        "id": row[0],
        "name": row[1],
        "owner": row[2],
        "type": row[3],
        "phone": row[4],
        "wilaya": row[5],
        "lat": row[6],
        "lng": row[7],
        "chat_id": row[8]

    }
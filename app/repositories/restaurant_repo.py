from app.core.db import get_cursor


# ================= GET ALL =================
def get_all_restaurants():
    cur = get_cursor()

    cur.execute("""
        SELECT name
        FROM restaurants
        ORDER BY id DESC
    """)

    return [r[0] for r in cur.fetchall()]


# ================= EXISTS =================
def exists(name):
    cur = get_cursor()

    cur.execute("""
        SELECT 1
        FROM restaurants
        WHERE LOWER(name)=LOWER(%s)
    """, (name,))

    return cur.fetchone() is not None


# ================= SAVE =================
def save(data):
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
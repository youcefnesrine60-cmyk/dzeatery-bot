from database.db import cursor, conn

def add_restaurant(data):
    cursor.execute("""
        INSERT INTO restaurants (name, owner, phone, wilaya, lat, lng, type, chat_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"], data["owner"], data["phone"],
        data["wilaya"], data["lat"], data["lng"],
        data["type"], data["chat_id"]
    ))
    conn.commit()


def exists(name):
    cursor.execute("SELECT 1 FROM restaurants WHERE name=?", (name,))
    return cursor.fetchone() is not None
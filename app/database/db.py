import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        owner TEXT,
        phone TEXT,
        wilaya TEXT,
        lat REAL,
        lng REAL,
        type TEXT,
        chat_id INTEGER
    )
    """)
    conn.commit()
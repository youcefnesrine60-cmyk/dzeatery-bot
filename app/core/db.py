# ==============================================
# 🐘 POSTGRESQL CONNECTION
# ==============================================

import os

import psycopg2

from dotenv import load_dotenv

from app.core.logger import (
    logger
)

# ==============================================
# 🌍 LOAD ENVIRONMENT VARIABLES
# ==============================================

load_dotenv()

# ==============================================
# 🌍 DATABASE URL
# ==============================================

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# ==============================================
# 🔌 GLOBAL CONNECTION
# ==============================================

conn = None

# ==============================================
# 🚀 CONNECT TO POSTGRESQL
# ==============================================

try:

    conn = psycopg2.connect(
        DATABASE_URL
    )

    logger.info(
        "PostgreSQL connected successfully."
    )

except Exception as e:

    logger.error(
        f"PostgreSQL connection failed: {e}"
    )

# ==============================================
# 📥 GET DATABASE CURSOR
# ==============================================

def get_cursor() -> psycopg2.extensions.cursor:

    global conn

    # ==========================================
    # 🔄 RECONNECT IF CONNECTION CLOSED
    # ==========================================

    if conn is None or conn.closed:

        logger.warning(
            "PostgreSQL connection lost. Reconnecting..."
        )

        conn = psycopg2.connect(
            DATABASE_URL
        )

        logger.info(
            "PostgreSQL reconnected successfully."
        )

    logger.info(
        "Fetching database cursor"
    )

    return conn.cursor()

# ==============================================
# ✅ COMMIT TRANSACTION
# ==============================================

def commit() -> None:

    if not conn:

        logger.warning(
            "Commit skipped: PostgreSQL unavailable."
        )

        return

    conn.commit()

# ==============================================
# ❌ ROLLBACK TRANSACTION
# ==============================================

def rollback() -> None:

    if not conn:

        logger.warning(
            "Rollback skipped: PostgreSQL unavailable."
        )

        return

    conn.rollback()

# ==============================================
# 🔒 CLOSE CONNECTION
# ==============================================

def close_connection() -> None:

    global conn

    if conn:

        conn.close()

        logger.info(
            "PostgreSQL connection closed."
        )

        conn = None
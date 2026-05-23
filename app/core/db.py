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
# 🌍 LOAD ENV
# ==============================================

load_dotenv()

# ==============================================
# 🌍 DATABASE URL
# ==============================================

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# ==============================================
# 🔌 CONNECTION
# ==============================================

conn = None

try:

    conn = psycopg2.connect(

        DATABASE_URL
    )

    conn.autocommit = True

    logger.info(
        "PostgreSQL connected successfully."
    )

except Exception as e:

    logger.error(
        f"PostgreSQL connection failed: {e}"
    )

# ==============================================
# 📥 GET CURSOR
# ==============================================

def get_cursor() -> psycopg2.extensions.cursor:

    if not conn:

        raise Exception(
            "PostgreSQL connection is not available."
        )

    logger.info(
        "Fetching database cursor"
    )

    return conn.cursor()

# ==============================================
# ✅ COMMIT
# ==============================================

def commit() -> None:

    if not conn:

        logger.warning(
            "Commit skipped: PostgreSQL unavailable."
        )

        return

    conn.commit()

# ==============================================
# ❌ ROLLBACK
# ==============================================

def rollback() -> None:

    if not conn:

        logger.warning(
            "Rollback skipped: PostgreSQL unavailable."
        )

        return

    conn.rollback()

# ==============================================
# ❌ CLOSE CONNECTION
# ==============================================

def close_connection() -> None:

    global conn

    if conn:

        conn.close()

        logger.info(
            "PostgreSQL connection closed."
        )

        conn = None
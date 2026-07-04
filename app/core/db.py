# ==============================================
# 🐘 POSTGRESQL DATABASE
# Psycopg3 (Async) + FastAPI
# Production Ready
# ==============================================

import os

from dotenv import load_dotenv

from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

from app.core.logger import logger

# ==============================================
# 🌍 LOAD ENVIRONMENT VARIABLES
# ==============================================

load_dotenv()

# ==============================================
# 🌍 DATABASE URL
# ==============================================

DATABASE_URL = os.getenv("DATABASE_URL")

# ==============================================
# 🧩 TYPES
# ==============================================

DatabasePool = AsyncConnectionPool

# ==============================================
# 🔌 GLOBAL POOL
# ==============================================

db_pool: DatabasePool | None = None

# ==============================================
# 🚀 INITIALIZE DATABASE POOL
# ==============================================

async def init_db() -> None:
    global db_pool

    if db_pool is not None:
        return

    try:
        db_pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            min_size=5,
            max_size=20,
            timeout=60,
            kwargs={
                "row_factory": dict_row,
            },
        )

        await db_pool.open()

        logger.info("postgresql_pool_initialized")

    except Exception as e:
        logger.exception(
            "postgresql_pool_init_failed",
            extra={"error": str(e)},
        )
        raise

# ==============================================
# 📥 GET POOL
# ==============================================

async def get_pool() -> DatabasePool:
    global db_pool

    if db_pool is None:
        await init_db()

    return db_pool

# ==============================================
# 📥 FETCH ONE
# ==============================================

async def fetchrow(query: str, *args):
    pool = await get_pool()

    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, args)
            return await cur.fetchone()

# ==============================================
# 📥 FETCH MANY
# ==============================================

async def fetch(query: str, *args):
    pool = await get_pool()

    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, args)
            return await cur.fetchall()

# ==============================================
# ✏️ EXECUTE
# ==============================================

async def execute(query: str, *args):
    pool = await get_pool()

    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, args)
            return cur.statusmessage

# ==============================================
# ➕ INSERT RETURNING ID
# ==============================================

async def insert_returning_id(query: str, *args) -> int:
    pool = await get_pool()

    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, args)
            value = await cur.fetchone()
            return int(value[0])

# ==============================================
# 🔄 TRANSACTION CONTEXT
# ==============================================

from contextlib import asynccontextmanager

@asynccontextmanager
async def transaction():
    pool = await get_pool()

    async with pool.connection() as conn:
        async with conn.transaction():
            yield conn

# ==============================================
# 🔒 CLOSE DATABASE POOL
# ==============================================

async def close_db() -> None:
    global db_pool

    if db_pool is None:
        return

    await db_pool.close()
    db_pool = None

    logger.info("postgresql_pool_closed")
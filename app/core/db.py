# ==============================================
# 🐘 POSTGRESQL DATABASE
# Psycopg3 (Async) + FastAPI
# Production Ready
# ==============================================

import os
import asyncio

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
            min_size=2,
            max_size=10,
            timeout=120,  # ✅ زيادة المهلة
            kwargs={
                "row_factory": dict_row,
                "connect_timeout": 30,  # ✅ إضافة مهلة الاتصال
                "keepalives": 1,
                "keepalives_idle": 10,
                "keepalives_interval": 5,
                "keepalives_count": 5,
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
# 📥 FETCH ONE (مع إعادة المحاولة)
# ==============================================

async def fetchrow(query: str, *args, retries: int = 3):
    """
    تنفيذ استعلام وإعادة صف واحد مع إعادة المحاولة عند فشل الاتصال
    
    Args:
        query: استعلام SQL
        *args: معاملات الاستعلام
        retries: عدد محاولات إعادة المحاولة (افتراضي 3)
        
    Returns:
        الصف المسترجع أو None
    """
    last_error = None
    
    for attempt in range(retries):
        try:
            pool = await get_pool()
            
            async with pool.connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, args)
                    return await cur.fetchone()
                    
        except Exception as e:
            last_error = e
            logger.warning(
                f"fetchrow_attempt_{attempt + 1}_failed",
                extra={
                    "error": str(e),
                    "attempt": attempt + 1,
                    "query": query[:100],  # تسجيل جزء من الاستعلام فقط
                },
            )
            
            # إذا كانت هذه ليست المحاولة الأخيرة، انتظر قبل إعادة المحاولة
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # 1, 2, 4 ثواني
                logger.info(
                    f"fetchrow_retry_in_{wait_time}s",
                    extra={"attempt": attempt + 1, "wait_time": wait_time},
                )
                await asyncio.sleep(wait_time)
    
    # إذا فشلت جميع المحاولات، أعد رفع الخطأ
    logger.error(
        "fetchrow_all_attempts_failed",
        extra={
            "query": query[:100],
            "retries": retries,
            "last_error": str(last_error),
        },
    )
    raise last_error

# ==============================================
# 📥 FETCH MANY (مع إعادة المحاولة)
# ==============================================

async def fetch(query: str, *args, retries: int = 3):
    """
    تنفيذ استعلام وإعادة عدة صفوف مع إعادة المحاولة عند فشل الاتصال
    
    Args:
        query: استعلام SQL
        *args: معاملات الاستعلام
        retries: عدد محاولات إعادة المحاولة (افتراضي 3)
        
    Returns:
        قائمة الصفوف المسترجعة
    """
    last_error = None
    
    for attempt in range(retries):
        try:
            pool = await get_pool()
            
            async with pool.connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(query, args)
                    return await cur.fetchall()
                    
        except Exception as e:
            last_error = e
            logger.warning(
                f"fetch_attempt_{attempt + 1}_failed",
                extra={
                    "error": str(e),
                    "attempt": attempt + 1,
                    "query": query[:100],
                },
            )
            
            if attempt < retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
    
    logger.error(
        "fetch_all_attempts_failed",
        extra={
            "query": query[:100],
            "retries": retries,
            "last_error": str(last_error),
        },
    )
    raise last_error

# ==============================================
# ✏️ EXECUTE (مع إعادة المحاولة)
# ==============================================

async def execute(query: str, *args, retries: int = 3):
    """
    تنفيذ استعلام SQL مع إعادة المحاولة عند فشل الاتصال
    
    Args:
        query: استعلام SQL
        *args: معاملات الاستعلام
        retries: عدد محاولات إعادة المحاولة (افتراضي 3)
        
    Returns:
        رسالة حالة التنفيذ
    """
    last_error = None
    
    for attempt in range(retries):
        try:
            pool = await get_pool()
            
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, args)
                    return cur.statusmessage
                    
        except Exception as e:
            last_error = e
            logger.warning(
                f"execute_attempt_{attempt + 1}_failed",
                extra={
                    "error": str(e),
                    "attempt": attempt + 1,
                    "query": query[:100],
                },
            )
            
            if attempt < retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
    
    logger.error(
        "execute_all_attempts_failed",
        extra={
            "query": query[:100],
            "retries": retries,
            "last_error": str(last_error),
        },
    )
    raise last_error

# ==============================================
# ➕ INSERT RETURNING ID (مع إعادة المحاولة)
# ==============================================

async def insert_returning_id(query: str, *args, retries: int = 3) -> int:
    """
    إدراج صف وإرجاع المعرف مع إعادة المحاولة عند فشل الاتصال
    
    Args:
        query: استعلام SQL (يجب أن يحتوي على RETURNING id)
        *args: معاملات الاستعلام
        retries: عدد محاولات إعادة المحاولة (افتراضي 3)
        
    Returns:
        المعرف المُدرج
    """
    last_error = None
    
    for attempt in range(retries):
        try:
            pool = await get_pool()
            
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, args)
                    value = await cur.fetchone()
                    return int(value[0])
                    
        except Exception as e:
            last_error = e
            logger.warning(
                f"insert_returning_id_attempt_{attempt + 1}_failed",
                extra={
                    "error": str(e),
                    "attempt": attempt + 1,
                    "query": query[:100],
                },
            )
            
            if attempt < retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
    
    logger.error(
        "insert_returning_id_all_attempts_failed",
        extra={
            "query": query[:100],
            "retries": retries,
            "last_error": str(last_error),
        },
    )
    raise last_error

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
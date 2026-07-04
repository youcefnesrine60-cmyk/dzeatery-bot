# ==============================================
# 👑 ADMIN REPOSITORY
# Async Psycopg3 Version
# ==============================================

from app.core.db import (
    fetch,
    fetchrow,
    insert_returning_id,
)
from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

Admin = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_ADMIN_SELECT = """
SELECT
    id,
    chat_id,
    username,
    full_name,
    role,
    password_hash,
    created_at,
    updated_at,
    is_active
FROM admins
"""

# ==============================================
# ➕ CREATE ADMIN
# ==============================================

async def create_admin(
    *,
    chat_id: int,
    username: str,
    full_name: str,
    role: str = "admin",
    password_hash: str | None = None,
) -> int:
    """
    إنشاء مسؤول جديد
    """
    admin_id = await insert_returning_id(
        """
        INSERT INTO admins
        (
            chat_id,
            username,
            full_name,
            role,
            password_hash
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        chat_id,
        username,
        full_name,
        role,
        password_hash,
    )

    logger.info(
        "admin_created",
        extra={
            "admin_id": admin_id,
            "chat_id": chat_id,
            "username": username,
        },
    )

    return admin_id

# ==============================================
# 🔍 GET ADMIN BY CHAT ID
# ==============================================

async def get_admin_by_chat_id(
    *,
    chat_id: int,
) -> Admin | None:
    """
    جلب بيانات المسؤول عن طريق معرف المحادثة
    """
    row = await fetchrow(
        _ADMIN_SELECT + """
        WHERE chat_id = %s
        AND is_active = TRUE
        """,
        chat_id,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# 🔍 GET ADMIN BY USERNAME
# ==============================================

async def get_admin_by_username(
    *,
    username: str,
) -> Admin | None:
    """
    جلب بيانات المسؤول عن طريق اسم المستخدم
    """
    row = await fetchrow(
        _ADMIN_SELECT + """
        WHERE username = %s
        AND is_active = TRUE
        """,
        username,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# 🔍 CHECK IF ADMIN EXISTS
# ==============================================

async def admin_exists(
    *,
    chat_id: int,
) -> bool:
    """
    التحقق من وجود مسؤول
    """
    row = await fetchrow(
        """
        SELECT 1
        FROM admins
        WHERE chat_id = %s
        AND is_active = TRUE
        """,
        chat_id,
    )

    return row is not None

# ==============================================
# ✅ GET ALL ADMINS
# ==============================================

async def get_all_admins() -> list[Admin]:
    """
    جلب جميع المسؤولين
    """
    rows = await fetch(
        _ADMIN_SELECT + """
        WHERE is_active = TRUE
        ORDER BY id ASC
        """
    )

    return [dict(row) for row in rows]
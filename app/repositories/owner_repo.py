# ==============================================
# 👤 OWNER REPOSITORY
# Async Psycopg3 Version
# ==============================================

from datetime import datetime

from app.core.db import (
    execute,
    fetch,
    fetchrow,
    insert_returning_id,
)

from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

Owner = dict[str, object]

# ==============================================
# 🧩 BASE SELECT
# ==============================================

_OWNER_SELECT = """
SELECT
    id,
    chat_id,
    full_name,
    phone,
    email,
    registration_status,
    trial_used,
    created_at
FROM owners
"""

# ==============================================
# ➕ CREATE OWNER
# ==============================================

async def create_owner(
    *,
    chat_id: int,
    full_name: str,
    phone: str,
    email: str,
) -> int:

    owner_id = await insert_returning_id(
        """
        INSERT INTO owners
        (
            chat_id,
            full_name,
            phone,
            email
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        chat_id,
        full_name,
        phone,
        email,
    )

    logger.info(
        "owner_created",
        extra={
            "owner_id": owner_id,
            "chat_id": chat_id,
        },
    )

    return owner_id


# ==============================================
# 🔍 GET OWNER BY ID
# ==============================================

async def get_owner_by_id(
    *,
    owner_id: int,
) -> Owner | None:
    
    """
    جلب بيانات المالك عن طريق المعرف
    
    Args:
        owner_id: معرف المالك
        
    Returns:
        Owner | None: بيانات المالك أو None
    """

    row = await fetchrow(
        _OWNER_SELECT + """
        WHERE id = %s
        """,
        owner_id,
    )

    if not row:

        logger.warning(
            "owner_not_found_by_id",
            extra={
                "owner_id": owner_id,
            },
        )
        return None

    return dict(row)


# ==============================================
# 🔍 GET OWNER CREATED AT
# ==============================================

async def get_owner_created_at(
    *,
    owner_id: int,
) -> datetime | None:
    """
    جلب تاريخ إنشاء المالك
    
    Args:
        owner_id: معرف المالك
        
    Returns:
        datetime | None: تاريخ الإنشاء أو None
    """
    row = await fetchrow(
        """
        SELECT created_at
        FROM owners
        WHERE id = %s
        """,
        owner_id,
    )

    if not row:
        return None

    return row["created_at"]


# ==============================================
# 🔍 GET OWNER BY CHAT ID
# ==============================================

async def get_owner_by_chat_id(
    *,
    chat_id: int,
) -> Owner | None:

    row = await fetchrow(
        _OWNER_SELECT + """
        WHERE chat_id = %s
        """,
        chat_id,
    )

    if not row:
        return None

    return dict(row)


# ==============================================
# 🔍 OWNER EXISTS
# ==============================================

async def owner_exists(
    *,
    chat_id: int,
) -> bool:

    row = await fetchrow(
        """
        SELECT 1
        FROM owners
        WHERE chat_id = %s
        """,
        chat_id,
    )

    exists = row is not None

    logger.info(
        "owner_exists_checked",
        extra={
            "chat_id": chat_id,
            "exists": exists,
        },
    )

    return exists


# ==============================================
# ✅ UPDATE REGISTRATION STATUS
# ==============================================

async def update_registration_status(
    *,
    owner_id: int,
    status: str,
) -> None:

    await execute(
        """
        UPDATE owners
        SET registration_status = %s
        WHERE id = %s
        """,
        status,
        owner_id,
    )

    logger.info(
        "owner_registration_status_updated",
        extra={
            "owner_id": owner_id,
            "status": status,
        },
    )


# ==============================================
# 🎁 MARK TRIAL AS USED
# ==============================================

async def mark_trial_used(
    *,
    owner_id: int,
) -> None:

    await execute(
        """
        UPDATE owners
        SET trial_used = TRUE
        WHERE id = %s
        """,
        owner_id,
    )

    logger.info(
        "owner_trial_marked_used",
        extra={
            "owner_id": owner_id,
        },
    )


# ==============================================
# 🔍 HAS USED TRIAL
# ==============================================

async def has_used_trial(
    *,
    owner_id: int,
) -> bool:

    row = await fetchrow(
        """
        SELECT trial_used
        FROM owners
        WHERE id = %s
        """,
        owner_id,
    )

    if not row:
        return False

    return bool(row["trial_used"])


# ==============================================
# 📥 GET ALL OWNERS
# ==============================================

async def get_all_owners() -> list[Owner]:

    rows = await fetch(
        _OWNER_SELECT + """
        ORDER BY id DESC
        """
    )

    owners = [dict(row) for row in rows]

    logger.info(
        "owners_fetched",
        extra={
            "count": len(owners),
        },
    )

    return owners
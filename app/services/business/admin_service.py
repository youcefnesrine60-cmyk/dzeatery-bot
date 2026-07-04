# ==============================================
# 👑 ADMIN SERVICE
# Business Logic Layer
# ==============================================

from app.core.logger import logger

from app.repositories.admin_repo import (
    create_admin,
    get_admin_by_chat_id,
    admin_exists,
    get_all_admins,
)

# ==============================================
# 👑 GET OR CREATE ADMIN
# ==============================================

async def get_or_create_admin(
    *,
    chat_id: int,
    username: str,
    full_name: str,
) -> int:
    """
    جلب المسؤول أو إنشاؤه إذا لم يكن موجوداً
    """
    # التحقق من وجود المسؤول
    existing = await get_admin_by_chat_id(
        chat_id=chat_id,
    )

    if existing:
        logger.info(
            "admin_already_exists",
            extra={
                "admin_id": existing["id"],
                "chat_id": chat_id,
            },
        )
        return existing["id"]

    # إنشاء مسؤول جديد
    admin_id = await create_admin(
        chat_id=chat_id,
        username=username,
        full_name=full_name,
    )

    logger.info(
        "admin_created_from_service",
        extra={
            "admin_id": admin_id,
            "chat_id": chat_id,
        },
    )

    return admin_id

# ==============================================
# 🔍 IS ADMIN
# ==============================================

async def is_admin(
    *,
    chat_id: int,
) -> bool:
    """
    التحقق مما إذا كان المستخدم مسؤولاً
    """
    return await admin_exists(
        chat_id=chat_id,
    )


# ==============================================
# 📥 GET ADMIN
# ==============================================

async def get_admin(
    *,
    chat_id: int,
) -> dict | None:
    """
    جلب بيانات المسؤول
    """
    return await get_admin_by_chat_id(
        chat_id=chat_id,
    )


# ==============================================
# 📥 GET ALL ADMINS
# ==============================================

async def get_all_admins_list() -> list[dict]:
    """
    جلب جميع المسؤولين
    """
    return await get_all_admins()


# ==============================================
# 🔢 COUNT ADMINS
# ==============================================

async def count_admins() -> int:
    """
    حساب عدد المسؤولين
    """
    admins = await get_all_admins()
    return len(admins)
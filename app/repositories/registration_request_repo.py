# ==============================================
# 📝 REGISTRATION REQUEST REPOSITORY
# Async Psycopg3 Version
# إنشاء طلب
#    ↓
# استلام الطلب
#    ↓
# الموافقة على الطلب
#    ↓
# رفض الطلب
#    ↓
# حذف الطلب
# ==============================================

from app.core.db import (
    execute, 
    fetch, 
    fetchrow, 
    insert_returning_id
)

from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

RegistrationRequest = dict[str, object]

# ==============================================
# ➕ CREATE REGISTRATION REQUEST
# ==============================================

async def create_registration_request(
    *,
    chat_id: int,
    full_name: str,
    owner_phone: str,
    email: str | None,
    restaurant_name: str,
    restaurant_type: str,
    restaurant_phone: str,
    wilaya: str,
    lat: float,
    lng: float,
) -> int:

    request_id = await insert_returning_id(
        """
        INSERT INTO registration_requests (
            chat_id,
            full_name,
            owner_phone,
            email,
            restaurant_name,
            restaurant_type,
            restaurant_phone,
            wilaya,
            lat,
            lng
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
        """,
        chat_id,
        full_name,
        owner_phone,
        email,
        restaurant_name,
        restaurant_type,
        restaurant_phone,
        wilaya,
        lat,
        lng,
    )

    logger.info(
        "registration_request_created",
        extra={
            "request_id": request_id,
            "chat_id": chat_id,
        },
    )

    return request_id


# ==============================================
# 🔍 BASE SELECT
# ==============================================

_REGISTRATION_SELECT = """
SELECT
    id,
    chat_id,
    full_name,
    owner_phone,
    email,
    restaurant_name,
    restaurant_type,
    restaurant_phone,
    wilaya,
    lat,
    lng,
    status,
    created_at
FROM registration_requests
"""


def _row_to_dict(row) -> RegistrationRequest:
    return {
        "id": row["id"],
        "chat_id": row["chat_id"],
        "full_name": row["full_name"],
        "owner_phone": row["owner_phone"],
        "email": row["email"],
        "restaurant_name": row["restaurant_name"],
        "restaurant_type": row["restaurant_type"],
        "restaurant_phone": row["restaurant_phone"],
        "wilaya": row["wilaya"],
        "lat": row["lat"],
        "lng": row["lng"],
        "status": row["status"],
        "created_at": row["created_at"],
    }


# ==============================================
# 🔍 GET REQUEST BY ID
# ==============================================

async def get_registration_request_by_id(
    *,
    request_id: int,
) -> RegistrationRequest | None:

    row = await fetchrow(
        _REGISTRATION_SELECT + " WHERE id = %s",
        request_id,
    )

    return _row_to_dict(row) if row else None


# ==============================================
# 🔍 GET REQUEST BY CHAT ID
# ==============================================

async def get_registration_request_by_chat_id(
    *,
    chat_id: int,
) -> RegistrationRequest | None:

    row = await fetchrow(
        _REGISTRATION_SELECT + """
        WHERE chat_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        chat_id,
    )

    return _row_to_dict(row) if row else None


# ==============================================
# 🔍 GET PENDING REQUESTS
# ==============================================

async def get_pending_requests() -> list[RegistrationRequest]:

    rows = await fetch(
        _REGISTRATION_SELECT + """
        WHERE status = 'pending'
        ORDER BY id ASC
        """
    )

    requests = [_row_to_dict(row) for row in rows]

    logger.info(
        "pending_requests_fetched",
        extra={"count": len(requests)},
    )

    return requests


# ==============================================
# ✅ APPROVE REQUEST
# ==============================================

async def approve_registration_request(
    *,
    request_id: int,
) -> None:

    await execute(
        """
        UPDATE registration_requests
        SET status = 'approved'
        WHERE id = %s
        """,
        request_id,
    )

    logger.info(
        "registration_request_approved",
        extra={"request_id": request_id},
    )


# ==============================================
# ❌ REJECT REQUEST
# ==============================================

async def reject_registration_request(
    *,
    request_id: int,
) -> None:

    await execute(
        """
        UPDATE registration_requests
        SET status = 'rejected'
        WHERE id = %s
        """,
        request_id,
    )

    logger.info(
        "registration_request_rejected",
        extra={"request_id": request_id},
    )


# ==============================================
# 🗑️ DELETE REQUEST
# ==============================================

async def delete_registration_request(
    *,
    request_id: int,
) -> None:

    await execute(
        """
        DELETE FROM registration_requests
        WHERE id = %s
        """,
        request_id,
    )

    logger.info(
        "registration_request_deleted",
        extra={"request_id": request_id},
    )
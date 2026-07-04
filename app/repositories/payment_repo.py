# ==============================================
# 💳 PAYMENT REPOSITORY
# Async Psycopg3 Version
# ==============================================

from datetime import datetime
from psycopg import AsyncConnection

from app.core.logger import logger

from app.core.db import (
    execute,
    fetch,
    fetchrow,
    insert_returning_id,
)

# ==============================================
# 🧩 TYPES
# ==============================================

Payment = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_PAYMENT_SELECT = """
SELECT
    id,
    owner_id,
    restaurant_id,
    subscription_id,
    payment_method,
    amount,
    status,
    external_reference,
    created_at,
    paid_at
FROM payments
"""

# ==============================================
# 🧩 ROW MAPPER
# ==============================================

def _row_to_payment(row: dict) -> Payment:
    return {
        "id": row["id"],
        "owner_id": row["owner_id"],
        "restaurant_id": row["restaurant_id"],
        "subscription_id": row["subscription_id"],
        "payment_method": row["payment_method"],
        "amount": row["amount"],
        "status": row["status"],
        "external_reference": row["external_reference"],
        "created_at": row["created_at"],
        "paid_at": row["paid_at"],
    }

# ==============================================
# ➕ CREATE PAYMENT
# ==============================================

async def create_payment(
    *,
    owner_id: int,
    restaurant_id: int,
    subscription_id: int | None,
    payment_method: str,
    amount: float,
    status: str = "pending",
    external_reference: str | None = None,
) -> int:

    payment_id = await insert_returning_id(
        """
        INSERT INTO payments
        (
            owner_id,
            restaurant_id,
            subscription_id,
            payment_method,
            amount,
            status,
            external_reference
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        owner_id,
        restaurant_id,
        subscription_id,
        payment_method,
        amount,
        status,
        external_reference,
    )

    logger.info(
        "payment_created",
        extra={
            "payment_id": payment_id,
            "owner_id": owner_id,
            "restaurant_id": restaurant_id,
        },
    )

    return payment_id

# ==============================================
# 🔍 GET PAYMENT BY ID
# ==============================================

async def get_payment_by_id(
    *,
    payment_id: int,
) -> Payment | None:

    row = await fetchrow(
        _PAYMENT_SELECT + " WHERE id = %s",
        payment_id,
    )

    if not row:
        return None

    return _row_to_payment(row)

# ==============================================
# 🔍 GET PAYMENT BY REFERENCE
# ==============================================

async def get_payment_by_reference(
    *,
    external_reference: str,
) -> Payment | None:

    row = await fetchrow(
        _PAYMENT_SELECT + " WHERE external_reference = %s",
        external_reference,
    )

    if not row:
        return None

    return _row_to_payment(row)

# ==============================================
# ✅ MARK PAYMENT AS PAID
# ==============================================

async def mark_payment_paid(
    *,
    payment_id: int,
    paid_at: datetime,
) -> None:

    await execute(
        """
        UPDATE payments
        SET
            status = 'paid',
            paid_at = %s
        WHERE id = %s
        AND status = 'pending'
        """,
        paid_at,
        payment_id,
    )

    logger.info(
        "payment_marked_paid",
        extra={"payment_id": payment_id},
    )

# ==============================================
# ❌ MARK PAYMENT FAILED
# ==============================================

async def mark_payment_failed(
    *,
    payment_id: int,
) -> None:

    await execute(
        """
        UPDATE payments
        SET status = 'failed'
        WHERE id = %s
        """,
        payment_id,
    )

    logger.info(
        "payment_marked_failed",
        extra={"payment_id": payment_id},
    )

# ==============================================
# 🚫 CANCEL PAYMENT
# ==============================================

async def cancel_payment(
    *,
    payment_id: int,
) -> None:

    await execute(
        """
        UPDATE payments
        SET status = 'cancelled'
        WHERE id = %s
        """,
        payment_id,
    )

    logger.info(
        "payment_cancelled",
        extra={"payment_id": payment_id},
    )

# ==============================================
# 🔍 GET OWNER PAYMENTS
# ==============================================

async def get_owner_payments(
    *,
    owner_id: int,
) -> list[Payment]:

    rows = await fetch(
        _PAYMENT_SELECT + """
        WHERE owner_id = %s
        ORDER BY id DESC
        """,
        owner_id,
    )

    return [_row_to_payment(row) for row in rows]

# ==============================================
# 🔍 GET RESTAURANT PAYMENTS
# ==============================================

async def get_restaurant_payments(
    *,
    restaurant_id: int,
) -> list[Payment]:

    rows = await fetch(
        _PAYMENT_SELECT + """
        WHERE restaurant_id = %s
        ORDER BY id DESC
        """,
        restaurant_id,
    )

    return [_row_to_payment(row) for row in rows]

# ==============================================
# ✅ MARK PAYMENT PAID (TX)
# ==============================================

async def confirm_payment_tx(
    *,
    conn: AsyncConnection,
    payment_id: int,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            UPDATE payments
            SET
                status = 'paid',
                paid_at = NOW()
            WHERE id = %s
            AND status = 'pending'
            """,
            (
                payment_id,
            ),
        )

        return cur.rowcount

# ==============================================
# ❌ MARK PAYMENT FAILED (TX)
# ==============================================

async def fail_payment_tx(
    *,
    conn: AsyncConnection,
    payment_id: int,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            UPDATE payments
            SET status = 'failed'
            WHERE id = %s
            """,
            (
                payment_id,
            ),
        )
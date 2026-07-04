# ==============================================
# 💳 ORDER PAYMENTS REPOSITORY
# Async Psycopg3 Version
# ==============================================

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

OrderPayment = dict[str, object]

# ==============================================
# 📥 BASE SELECT
# ==============================================

BASE_SELECT = """
SELECT
    id,
    order_id,
    payment_method,
    payment_status,
    amount,
    transaction_reference,
    paid_at,
    created_at
FROM order_payments
"""

# ==============================================
# ➕ CREATE PAYMENT
# ==============================================

async def create_order_payment(
    *,
    order_id: int,
    payment_method: str,
    payment_status: str,
    amount: float,
    transaction_reference: str | None = None,
) -> int:

    payment_id = await insert_returning_id(
        """
        INSERT INTO order_payments
        (
            order_id,
            payment_method,
            payment_status,
            amount,
            transaction_reference
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
        order_id,
        payment_method,
        payment_status,
        amount,
        transaction_reference,
    )

    logger.info(
        "order_payment_created",
        extra={
            "payment_id": payment_id,
            "order_id": order_id,
        },
    )

    return payment_id

# ==============================================
# 🔍 GET PAYMENT
# ==============================================

async def get_order_payment(
    *,
    payment_id: int,
) -> OrderPayment | None:

    row = await fetchrow(
        f"""
        {BASE_SELECT}
        WHERE id = %s
        """,
        payment_id,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# 🔍 GET ORDER PAYMENTS
# ==============================================

async def get_order_payments(
    *,
    order_id: int,
) -> list[OrderPayment]:

    rows = await fetch(
        f"""
        {BASE_SELECT}
        WHERE order_id = %s
        ORDER BY id
        """,
        order_id,
    )

    return [
        dict(row)
        for row in rows
    ]

# ==============================================
# 🔍 GET PAYMENT BY REFERENCE
# ==============================================

async def get_payment_by_reference(
    *,
    transaction_reference: str,
) -> OrderPayment | None:

    row = await fetchrow(
        f"""
        {BASE_SELECT}
        WHERE transaction_reference = %s
        """,
        transaction_reference,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# ✅ MARK AS PAID
# ==============================================

async def mark_payment_paid(
    *,
    payment_id: int,
) -> None:

    await execute(
        """
        UPDATE order_payments
        SET
            payment_status = 'paid',
            paid_at = NOW()
        WHERE id = %s
        """,
        payment_id,
    )

    logger.info(
        "order_payment_paid",
        extra={
            "payment_id": payment_id,
        },
    )

# ==============================================
# ❌ MARK AS FAILED
# ==============================================

async def mark_payment_failed(
    *,
    payment_id: int,
) -> None:

    await execute(
        """
        UPDATE order_payments
        SET
            payment_status = 'failed'
        WHERE id = %s
        """,
        payment_id,
    )

    logger.info(
        "order_payment_failed",
        extra={
            "payment_id": payment_id,
        },
    )

# ==============================================
# 🚫 MARK AS CANCELLED
# ==============================================

async def mark_payment_cancelled(
    *,
    payment_id: int,
) -> None:

    await execute(
        """
        UPDATE order_payments
        SET
            payment_status = 'cancelled'
        WHERE id = %s
        """,
        payment_id,
    )

    logger.info(
        "order_payment_cancelled",
        extra={
            "payment_id": payment_id,
        },
    )

# ==============================================
# 🗑 DELETE PAYMENT
# ==============================================

async def delete_order_payment(
    *,
    payment_id: int,
) -> None:

    await execute(
        """
        DELETE FROM order_payments
        WHERE id = %s
        """,
        payment_id,
    )

    logger.info(
        "order_payment_deleted",
        extra={
            "payment_id": payment_id,
        },
    )
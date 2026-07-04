# ==============================================
# 📜 ORDER STATUS HISTORY REPOSITORY
# Async Psycopg3 Version
# ==============================================

from psycopg import AsyncConnection

from app.core.db import (
    execute,
    fetch,
)

from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

OrderStatusHistory = dict[str, object]

# ==============================================
# 📥 BASE SELECT
# ==============================================

BASE_SELECT = """
SELECT
    id,
    order_id,
    old_status,
    new_status,
    changed_by_employee_id,
    note,
    created_at
FROM order_status_history
"""

# ==============================================
# ➕ CREATE STATUS HISTORY
# ==============================================

async def create_status_history(
    *,
    order_id: int,
    old_status: str | None,
    new_status: str,
    changed_by_employee_id: int | None = None,
    note: str | None = None,
) -> None:

    await execute(
        """
        INSERT INTO order_status_history
        (
            order_id,
            old_status,
            new_status,
            changed_by_employee_id,
            note
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        order_id,
        old_status,
        new_status,
        changed_by_employee_id,
        note,
    )

    logger.info(
        "order_status_history_created",
        extra={
            "order_id": order_id,
            "new_status": new_status,
        },
    )

# ==============================================
# ➕ CREATE STATUS HISTORY (TX)
# ==============================================

async def create_status_history_tx(
    conn: AsyncConnection,
    *,
    order_id: int,
    old_status: str | None,
    new_status: str,
    changed_by_employee_id: int | None = None,
    note: str | None = None,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            INSERT INTO order_status_history
            (
                order_id,
                old_status,
                new_status,
                changed_by_employee_id,
                note
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                order_id,
                old_status,
                new_status,
                changed_by_employee_id,
                note,
            ),
        )

# ==============================================
# 🔍 GET ORDER STATUS HISTORY
# ==============================================

async def get_order_status_history(
    *,
    order_id: int,
) -> list[OrderStatusHistory]:

    rows = await fetch(
        f"""
        {BASE_SELECT}
        WHERE order_id = %s
        ORDER BY id ASC
        """,
        order_id,
    )

    return [
        dict(row)
        for row in rows
    ]

# ==============================================
# 🔍 GET LAST STATUS CHANGE
# ==============================================

async def get_last_status_change(
    *,
    order_id: int,
) -> OrderStatusHistory | None:

    rows = await fetch(
        f"""
        {BASE_SELECT}
        WHERE order_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        order_id,
    )

    if not rows:
        return None

    return dict(rows[0])

# ==============================================
# 🔍 GET STATUS TIMELINE
# ==============================================

async def get_status_timeline(
    *,
    order_id: int,
) -> list[dict[str, object]]:

    rows = await fetch(
        """
        SELECT
            new_status,
            created_at
        FROM order_status_history
        WHERE order_id = %s
        ORDER BY id ASC
        """,
        order_id,
    )

    return [
        dict(row)
        for row in rows
    ]

# ==============================================
# 🔢 COUNT STATUS CHANGES
# ==============================================

async def count_status_changes(
    *,
    order_id: int,
) -> int:

    rows = await fetch(
        """
        SELECT COUNT(*) AS total
        FROM order_status_history
        WHERE order_id = %s
        """,
        order_id,
    )

    if not rows:
        return 0

    return int(
        rows[0]["total"]
    )

# ==============================================
# 🔍 GET ORDERS BY STATUS
# ==============================================

async def get_orders_reached_status(
    *,
    status: str,
) -> list[int]:

    rows = await fetch(
        """
        SELECT DISTINCT order_id
        FROM order_status_history
        WHERE new_status = %s
        ORDER BY order_id
        """,
        status,
    )

    return [
        int(row["order_id"])
        for row in rows
    ]
# ==============================================
# 📦 ORDERS REPOSITORY
# Async Psycopg3 Version
# ==============================================

from app.core.db import (
    execute,
    fetch,
    fetchrow,
    insert_returning_id,
)

from psycopg import AsyncConnection
from app.core.logger import logger

# ==============================================
# 🧩 TYPES
# ==============================================

Order = dict[str, object]

# ==============================================
# 📥 BASE SELECT
# ==============================================

BASE_SELECT = """
SELECT
    id,
    restaurant_id,
    branch_id,
    table_id,
    employee_id,
    order_number,
    order_type,
    customer_name,
    customer_phone,
    delivery_address,
    customer_note,
    status,
    subtotal_amount,
    discount_amount,
    tax_amount,
    delivery_amount,
    total_amount,
    created_at,
    updated_at
FROM orders
"""

# ==============================================
# ➕ CREATE ORDER
# ==============================================

async def create_order(
    *,
    restaurant_id: int,
    branch_id: int | None,
    table_id: int | None,
    employee_id: int | None,
    order_number: str,
    order_type: str,
    customer_name: str | None,
    customer_phone: str | None,
    delivery_address: str | None,
    customer_note: str | None,
    status: str,
    subtotal_amount: float,
    discount_amount: float,
    tax_amount: float,
    delivery_amount: float,
    total_amount: float,
) -> int:

    order_id = await insert_returning_id(
        """
        INSERT INTO orders
        (
            restaurant_id,
            branch_id,
            table_id,
            employee_id,
            order_number,
            order_type,
            customer_name,
            customer_phone,
            delivery_address,
            customer_note,
            status,
            subtotal_amount,
            discount_amount,
            tax_amount,
            delivery_amount,
            total_amount
        )
        VALUES
        (
            %s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s
        )
        RETURNING id
        """,
        restaurant_id,
        branch_id,
        table_id,
        employee_id,
        order_number,
        order_type,
        customer_name,
        customer_phone,
        delivery_address,
        customer_note,
        status,
        subtotal_amount,
        discount_amount,
        tax_amount,
        delivery_amount,
        total_amount,
    )

    logger.info(
        "order_created",
        extra={
            "order_id": order_id,
            "restaurant_id": restaurant_id,
        },
    )

    return order_id

# ==============================================
# 🔍 GET ORDER
# ==============================================

async def get_order(
    *,
    order_id: int,
) -> Order | None:

    row = await fetchrow(
        f"""
        {BASE_SELECT}
        WHERE id = %s
        """,
        order_id,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# 🔍 GET ORDER BY NUMBER
# ==============================================

async def get_order_by_number(
    *,
    restaurant_id: int,
    order_number: str,
) -> Order | None:

    row = await fetchrow(
        f"""
        {BASE_SELECT}
        WHERE restaurant_id = %s
        AND order_number = %s
        """,
        restaurant_id,
        order_number,
    )

    if not row:
        return None

    return dict(row)

# ==============================================
# 🔍 GET RESTAURANT ORDERS
# ==============================================

async def get_restaurant_orders(
    *,
    restaurant_id: int,
) -> list[Order]:

    rows = await fetch(
        f"""
        {BASE_SELECT}
        WHERE restaurant_id = %s
        ORDER BY id DESC
        """,
        restaurant_id,
    )

    return [dict(row) for row in rows]

# ==============================================
# 🔍 GET ORDERS BY STATUS
# ==============================================

async def get_orders_by_status(
    *,
    restaurant_id: int,
    status: str,
) -> list[Order]:

    rows = await fetch(
        f"""
        {BASE_SELECT}
        WHERE restaurant_id = %s
        AND status = %s
        ORDER BY id DESC
        """,
        restaurant_id,
        status,
    )

    return [dict(row) for row in rows]

# ==============================================
# 🔄 UPDATE ORDER STATUS
# ==============================================

async def update_order_status(
    *,
    order_id: int,
    status: str,
) -> None:

    await execute(
        """
        UPDATE orders
        SET
            status = %s,
            updated_at = NOW()
        WHERE id = %s
        """,
        status,
        order_id,
    )

# ==============================================
# 💰 UPDATE TOTALS
# ==============================================

async def update_order_totals(
    *,
    order_id: int,
    subtotal_amount: float,
    discount_amount: float,
    tax_amount: float,
    delivery_amount: float,
    total_amount: float,
) -> None:

    await execute(
        """
        UPDATE orders
        SET
            subtotal_amount = %s,
            discount_amount = %s,
            tax_amount = %s,
            delivery_amount = %s,
            total_amount = %s,
            updated_at = NOW()
        WHERE id = %s
        """,
        subtotal_amount,
        discount_amount,
        tax_amount,
        delivery_amount,
        total_amount,
        order_id,
    )

# ==============================================
# ❌ DELETE ORDER
# ==============================================

async def delete_order(
    *,
    order_id: int,
) -> None:

    await execute(
        """
        DELETE FROM orders
        WHERE id = %s
        """,
        order_id,
    )

    logger.info(
        "order_deleted",
        extra={
            "order_id": order_id,
        },
    )

# ==============================================
# 🔒 TX CREATE ORDER
# ==============================================

async def create_order_tx(
    *,
    conn: AsyncConnection,
    restaurant_id: int,
    branch_id: int | None,
    table_id: int | None,
    employee_id: int | None,
    order_number: str,
    order_type: str,
    customer_name: str | None,
    customer_phone: str | None,
    delivery_address: str | None,
    customer_note: str | None,
    status: str,
    subtotal_amount: float,
    discount_amount: float,
    tax_amount: float,
    delivery_amount: float,
    total_amount: float,
) -> int:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            INSERT INTO orders
            (
                restaurant_id,
                branch_id,
                table_id,
                employee_id,
                order_number,
                order_type,
                customer_name,
                customer_phone,
                delivery_address,
                customer_note,
                status,
                subtotal_amount,
                discount_amount,
                tax_amount,
                delivery_amount,
                total_amount
            )
            VALUES
            (
                %s,%s,%s,%s,
                %s,%s,%s,%s,
                %s,%s,%s,%s,
                %s,%s,%s,%s
            )
            RETURNING id
            """,
            (
                restaurant_id,
                branch_id,
                table_id,
                employee_id,
                order_number,
                order_type,
                customer_name,
                customer_phone,
                delivery_address,
                customer_note,
                status,
                subtotal_amount,
                discount_amount,
                tax_amount,
                delivery_amount,
                total_amount,
            ),
        )

        row = await cur.fetchone()

        return int(row[0])
    
# ==============================================
# 🔒 TX UPDATE ORDER TOTALS
# ==============================================

async def update_order_totals_tx(
    *,
    conn: AsyncConnection,
    order_id: int,
    subtotal_amount: float,
    discount_amount: float,
    tax_amount: float,
    delivery_amount: float,
    total_amount: float,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            UPDATE orders
            SET
                subtotal_amount = %s,
                discount_amount = %s,
                tax_amount = %s,
                delivery_amount = %s,
                total_amount = %s,
                updated_at = NOW()
            WHERE id = %s
            """,
            (
                subtotal_amount,
                discount_amount,
                tax_amount,
                delivery_amount,
                total_amount,
                order_id,
            ),
        )

# ==============================================
# 🔒 TX UPDATE ORDER STATUS
# ==============================================

async def update_order_status_tx(
    *,
    conn: AsyncConnection,
    order_id: int,
    status: str,
) -> None:

    async with conn.cursor() as cur:

        await cur.execute(
            """
            UPDATE orders
            SET
                status = %s,
                updated_at = NOW()
            WHERE id = %s
            """,
            (
                status,
                order_id,
            ),
        )
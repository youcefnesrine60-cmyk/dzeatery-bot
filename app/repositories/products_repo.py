# ==============================================
# 🍔 PRODUCTS REPOSITORY
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

Product = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_PRODUCT_SELECT = """
SELECT
    id,
    restaurant_id,
    category_id,
    name,
    description,
    price,
    image_url,
    is_available,
    sort_order,
    created_at
FROM products
"""

# ==============================================
# 🧩 ROW MAPPER
# ==============================================

def _row_to_product(row) -> Product:

    return {
        "id": row["id"],
        "restaurant_id": row["restaurant_id"],
        "category_id": row["category_id"],
        "name": row["name"],
        "description": row["description"],
        "price": float(row["price"]),
        "image_url": row["image_url"],
        "is_available": row["is_available"],
        "sort_order": row["sort_order"],
        "created_at": row["created_at"],
    }

# ==============================================
# ➕ CREATE PRODUCT
# ==============================================

async def create_product(
    *,
    restaurant_id: int,
    category_id: int,
    name: str,
    description: str | None,
    price: float,
    image_url: str | None = None,
    sort_order: int = 0,
) -> int:

    product_id = await insert_returning_id(
        """
        INSERT INTO products
        (
            restaurant_id,
            category_id,
            name,
            description,
            price,
            image_url,
            sort_order
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
        restaurant_id,
        category_id,
        name,
        description,
        price,
        image_url,
        sort_order,
    )

    logger.info(
        "product_created",
        extra={
            "product_id": product_id,
            "restaurant_id": restaurant_id,
        },
    )

    return product_id

# ==============================================
# 🔍 GET PRODUCT
# ==============================================

async def get_product_by_id(
    *,
    product_id: int,
) -> Product | None:

    row = await fetchrow(
        _PRODUCT_SELECT + """
        WHERE id = %s
        """,
        product_id,
    )

    return _row_to_product(row) if row else None

# ==============================================
# 🔍 GET RESTAURANT PRODUCTS
# ==============================================

async def get_restaurant_products(
    *,
    restaurant_id: int,
) -> list[Product]:

    rows = await fetch(
        _PRODUCT_SELECT + """
        WHERE restaurant_id = %s
        ORDER BY sort_order ASC, id ASC
        """,
        restaurant_id,
    )

    return [_row_to_product(r) for r in rows]

# ==============================================
# 🔍 COUNT PRODUCTS
# ==============================================

async def count_restaurant_products(
    *,
    restaurant_id: int,
) -> int:

    row = await fetchrow(
        """
        SELECT COUNT(*) AS total
        FROM products
        WHERE restaurant_id = %s
        """,
        restaurant_id,
    )

    return int(row["total"])

# ==============================================
# ✏️ UPDATE PRODUCT
# ==============================================

async def update_product(
    *,
    product_id: int,
    name: str,
    description: str | None,
    price: float,
    image_url: str | None,
    sort_order: int,
) -> None:

    await execute(
        """
        UPDATE products
        SET
            name = %s,
            description = %s,
            price = %s,
            image_url = %s,
            sort_order = %s
        WHERE id = %s
        """,
        name,
        description,
        price,
        image_url,
        sort_order,
        product_id,
    )

# ==============================================
# ✅ SET AVAILABILITY
# ==============================================

async def set_product_availability(
    *,
    product_id: int,
    is_available: bool,
) -> None:

    await execute(
        """
        UPDATE products
        SET is_available = %s
        WHERE id = %s
        """,
        is_available,
        product_id,
    )

# ==============================================
# ❌ DELETE PRODUCT
# ==============================================

async def delete_product(
    *,
    product_id: int,
) -> None:

    await execute(
        """
        DELETE FROM products
        WHERE id = %s
        """,
        product_id,
    )

    logger.info(
        "product_deleted",
        extra={
            "product_id": product_id,
        },
    )
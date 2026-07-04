# ==============================================
# 📂 CATEGORIES REPOSITORY
# ==============================================

from app.core.db import (
    fetch,
    fetchrow,
    execute,
    insert_returning_id,
)

from app.core.logger import logger

# ==============================================
# TYPES
# ==============================================

Category = dict[str, object]

# ==============================================
# ROW MAPPER
# ==============================================

def _row_to_category(row) -> Category:
    return {
        "id": row["id"],
        "restaurant_id": row["restaurant_id"],
        "name": row["name"],
        "sort_order": row["sort_order"],
        "created_at": row["created_at"],
    }


# ==============================================
# CREATE CATEGORY
# ==============================================

async def create_category(
    *,
    restaurant_id: int,
    name: str,
    sort_order: int = 0,
) -> int:

    category_id = await insert_returning_id(
        """
        INSERT INTO categories
        (
            restaurant_id,
            name,
            sort_order
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        restaurant_id,
        name,
        sort_order,
    )

    logger.info(
        "category_created",
        extra={
            "category_id": category_id,
            "restaurant_id": restaurant_id,
        },
    )

    return category_id


# ==============================================
# GET CATEGORY
# ==============================================

async def get_category_by_id(
    *,
    category_id: int,
) -> Category | None:

    row = await fetchrow(
        """
        SELECT *
        FROM categories
        WHERE id = %s
        """,
        category_id,
    )

    if not row:
        return None

    return _row_to_category(row)


# ==============================================
# GET RESTAURANT CATEGORIES
# ==============================================

async def get_restaurant_categories(
    *,
    restaurant_id: int,
) -> list[Category]:

    rows = await fetch(
        """
        SELECT *
        FROM categories
        WHERE restaurant_id = %s
        ORDER BY sort_order ASC, id ASC
        """,
        restaurant_id,
    )

    return [_row_to_category(row) for row in rows]


# ==============================================
# DELETE CATEGORY
# ==============================================

async def delete_category(
    *,
    category_id: int,
) -> None:

    await execute(
        """
        DELETE FROM categories
        WHERE id = %s
        """,
        category_id,
    )

    logger.info(
        "category_deleted",
        extra={"category_id": category_id},
    )
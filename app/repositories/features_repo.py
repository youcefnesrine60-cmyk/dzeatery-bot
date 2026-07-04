# ==============================================
# 🧩 FEATURES REPOSITORY
# مستودع الميزات داخل النظام
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

Feature = dict[str, object]

# ==============================================
# 🔍 BASE SELECT
# ==============================================

_FEATURE_SELECT = """
SELECT
    id,
    code,
    name,
    description
FROM features
"""

# ==============================================
# 🧩 ROW MAPPER
# ==============================================

def _row_to_feature(
    row: dict,
) -> Feature:

    return {
        "id": row["id"],
        "code": row["code"],
        "name": row["name"],
        "description": row["description"],
    }


# ==============================================
# ➕ CREATE FEATURE
# ==============================================

async def create_feature(
    *,
    code: str,
    name: str,
    description: str | None = None,
) -> int:

    feature_id = await insert_returning_id(
        """
        INSERT INTO features
        (
            code,
            name,
            description
        )
        VALUES
        (
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        code,
        name,
        description,
    )

    logger.info(
        "feature_created",
        extra={
            "feature_id": feature_id,
            "code": code,
        },
    )

    return feature_id


# ==============================================
# 🔍 GET FEATURE BY ID
# ==============================================

async def get_feature_by_id(
    *,
    feature_id: int,
) -> Feature | None:

    row = await fetchrow(
        _FEATURE_SELECT
        + """
        WHERE id = %s
        """,
        feature_id,
    )

    if not row:

        logger.warning(
            "feature_not_found",
            extra={
                "feature_id": feature_id,
            },
        )

        return None

    return _row_to_feature(row)


# ==============================================
# 🔍 GET FEATURE BY CODE
# ==============================================

async def get_feature_by_code(
    *,
    code: str,
) -> Feature | None:

    row = await fetchrow(
        _FEATURE_SELECT
        + """
        WHERE code = %s
        LIMIT 1
        """,
        code,
    )

    if not row:
        return None

    return _row_to_feature(row)


# ==============================================
# 🔍 GET ALL FEATURES
# ==============================================

async def get_all_features() -> list[Feature]:

    rows = await fetch(
        _FEATURE_SELECT
        + """
        ORDER BY id ASC
        """
    )

    features = [
        _row_to_feature(row)
        for row in rows
    ]

    logger.info(
        "features_fetched",
        extra={
            "count": len(features),
        },
    )

    return features


# ==============================================
# ✏️ UPDATE FEATURE
# ==============================================

async def update_feature(
    *,
    feature_id: int,
    name: str,
    description: str | None,
) -> None:

    await execute(
        """
        UPDATE features
        SET
            name = %s,
            description = %s
        WHERE id = %s
        """,
        name,
        description,
        feature_id,
    )

    logger.info(
        "feature_updated",
        extra={
            "feature_id": feature_id,
        },
    )


# ==============================================
# ❌ DELETE FEATURE
# ==============================================

async def delete_feature(
    *,
    feature_id: int,
) -> None:

    await execute(
        """
        DELETE FROM features
        WHERE id = %s
        """,
        feature_id,
    )

    logger.info(
        "feature_deleted",
        extra={
            "feature_id": feature_id,
        },
    )
# ==============================================
# 🧠 STATE HELPER
# دوال مساعدة لإدارة الحالة بشكل موحد
# ==============================================

from typing import Any

from app.core.logger import logger

from app.repositories.state_repo import (
    get_state,
    set_state,
)

# ==============================================
# 🧩 TYPES
# ==============================================

StateData = dict[str, Any]


# ==============================================
# 📥 GET STATE
# ==============================================

async def get_user_state(
    *,
    chat_id: int,
) -> StateData | None:
    """
    جلب حالة المستخدم
    """
    return await get_state(
        chat_id=chat_id
    )


# ==============================================
# 💾 UPDATE STATE FIELD
# ==============================================

async def update_state_field(
    *,
    chat_id: int,
    key: str,
    value: Any,
) -> None:
    """
    تحديث حقل معين في الحالة دون فقدان البيانات الأخرى
    """
    try:
        state = await get_state(
            chat_id=chat_id
        )

        if state is None:
            state = {}

        state[key] = value

        await set_state(
            chat_id=chat_id, 
            state=state
        )

        logger.debug(
            "state_field_updated",
            extra={
                "chat_id": chat_id,
                "key": key,
                "value": value,
            },
        )

    except Exception as e:
        logger.error(
            "state_field_update_failed",
            extra={
                "chat_id": chat_id,
                "key": key,
                "error": str(e),
            },
        )
        raise


# ==============================================
# 📥 APPEND TO STATE LIST
# ==============================================

async def append_to_state_list(
    *,
    chat_id: int,
    list_key: str,
    value: Any,
) -> None:
    """
    إضافة عنصر إلى قائمة في الحالة (مع منع التكرار)
    """
    try:
        # ✅ جلب الحالة الحالية
        state = await get_state(
            chat_id=chat_id
        )

        if state is None:
            state = {}

        # ✅ التأكد من وجود القائمة
        if list_key not in state:
            state[list_key] = []

        # ✅ منع إضافة message_id مكرر
        if value not in state[list_key]:
            state[list_key].append(value)

            # ✅ حفظ الحالة
            await set_state(
                chat_id=chat_id, 
                state=state
            )

            logger.debug(
                "state_list_appended",
                extra={
                    "chat_id": chat_id,
                    "list_key": list_key,
                    "value": value,
                    "list_length": len(state[list_key]),
                },
            )

    except Exception as e:
        logger.error(
            "state_list_append_failed",
            extra={
                "chat_id": chat_id,
                "list_key": list_key,
                "error": str(e),
            },
        )
        raise
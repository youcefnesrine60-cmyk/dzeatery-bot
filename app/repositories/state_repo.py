# ==============================================
# 🧠 STATE REPOSITORY
# ==============================================

import json

from app.core.redis_client import (
    redis_client,
    memory_storage
)

from app.core.logger import (
    logger
)

# ==============================================
# 🔑 STATE KEY BUILDER
# ==============================================

def _state_key(

    chat_id: int

) -> str:

    return f"user:{chat_id}"

# ==============================================
# 📥 GET STATE
# ==============================================

def get_state(

    *,

    chat_id: int

) -> dict | None:

    key = _state_key(

        chat_id = chat_id
    )

    # ==========================================
    # 🔴 REDIS
    # ==========================================

    if redis_client:

        logger.info(

            "getting_state_from_redis",

            extra={
                "chat_id": chat_id
            }
        )

        data = redis_client.get(key)

        if not data:

            logger.info(

                "state_not_found",

                extra={
                    "chat_id": chat_id
                }
            )

            return None

        logger.info(

            "state_loaded_from_redis",

            extra={
                "chat_id": chat_id
            }
        )

        return json.loads(data)

    # ==========================================
    # 🧠 MEMORY
    # ==========================================

    logger.info(

        "getting_state_from_memory",

        extra={
            "chat_id": chat_id
        }
    )

    return memory_storage.get(chat_id)

# ==============================================
# 💾 SET STATE
# ==============================================

def set_state(

    *,

    chat_id: int,

    state: dict

) -> None:

    key = _state_key(

        chat_id = chat_id
    )

    # ==========================================
    # 🔴 REDIS
    # ==========================================

    if redis_client:

        logger.info(

            "saving_state_to_redis",

            extra={
                "chat_id": chat_id
            }
        )

        redis_client.set(

            key,

            json.dumps(state)
        )

        logger.info(

            "state_saved_to_redis",

            extra={
                "chat_id": chat_id
            }
        )

        return

    # ==========================================
    # 🧠 MEMORY
    # ==========================================

    logger.info(

        "saving_state_to_memory",

        extra={
            "chat_id": chat_id
        }
    )

    memory_storage[chat_id] = state

# ==============================================
# 🗑️ DELETE STATE
# ==============================================

def delete_state(

    *,

    chat_id: int

) -> None:

    key = _state_key(

        chat_id = chat_id
    )

    # ==========================================
    # 🔴 REDIS
    # ==========================================

    if redis_client:

        logger.info(

            "deleting_state_from_redis",

            extra={
                "chat_id": chat_id
            }
        )

        redis_client.delete(key)

        logger.info(

            "state_deleted_from_redis",

            extra={
                "chat_id": chat_id
            }
        )

        return

    # ==========================================
    # 🧠 MEMORY
    # ==========================================

    logger.info(

        "deleting_state_from_memory",

        extra={
            "chat_id": chat_id
        }
    )

    memory_storage.pop(chat_id, None)
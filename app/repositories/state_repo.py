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
# 📥 GET STATE
# ==============================================

def get_state(
    chat_id: int
) -> dict | None:

    # ==========================================
    # 🔴 REDIS
    # ==========================================

    if redis_client:

        data = redis_client.get(
            f"user:{chat_id}"
        )

        if data:

            return json.loads(data)

        return None

    # ==========================================
    # 🧠 MEMORY
    # ==========================================

    return memory_storage.get(chat_id)

# ==============================================
# 💾 SET STATE
# ==============================================

def set_state(
    chat_id: int,
    state: dict
) -> None:

    logger.info(

        f"Setting state for user {chat_id}",

        extra={
            "chat_id": chat_id
        }
    )

    # ==========================================
    # 🔴 REDIS
    # ==========================================

    if redis_client:

        redis_client.set(

            f"user:{chat_id}",

            json.dumps(state)
        )

        return

    # ==========================================
    # 🧠 MEMORY
    # ==========================================

    memory_storage[chat_id] = state

# ==============================================
# 🗑️ DELETE STATE
# ==============================================

def delete_state(
    chat_id: int
) -> None:

    # ==========================================
    # 🔴 REDIS
    # ==========================================

    if redis_client:

        redis_client.delete(
            f"user:{chat_id}"
        )

        return

    # ==========================================
    # 🧠 MEMORY
    # ==========================================

    memory_storage.pop(chat_id, None)
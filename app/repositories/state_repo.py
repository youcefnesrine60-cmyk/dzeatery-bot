# ==============================================
# 🧠 STATE REPOSITORY
# ==============================================

import json

from app.core.redis_client import (
    redis_client
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

    data = redis_client.get(

        f"user:{chat_id}"
    )

    if data:

        logger.info(

            f"Retrieving state for user {chat_id}",

            extra={
                "chat_id": chat_id
            }
        )

        return json.loads(data)

    logger.warning(

        f"No state found for user {chat_id}",

        extra={
            "chat_id": chat_id
        }
    )

    return None

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
            "chat_id": chat_id,
            "state": state
        }
    )

    redis_client.set(

        f"user:{chat_id}",

        json.dumps(state)
    )

# ==============================================
# 🗑️ DELETE STATE
# ==============================================

def delete_state(
    chat_id: int
) -> None:

    logger.info(

        f"Deleting state for user {chat_id}",

        extra={
            "chat_id": chat_id
        }
    )

    redis_client.delete(

        f"user:{chat_id}"
    )
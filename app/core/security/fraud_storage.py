#================================
#  تخزين سجل الاحتيال
#================================

from app.core.redis_client import (
    redis_client
)

from app.core.logger import (
    logger
)

class FraudStorage:

    PREFIX = "fraud"

    @classmethod
    async def add_score(

        cls: type,

        chat_id: int,

        score: int
    ) -> None:
        
        if not redis_client:
            logger.warning(
                "Redis client is not initialized",
                extra={
                    "chat_id": chat_id
                }
            )
            return

        key = f"{cls.PREFIX}:{chat_id}"

        redis_client.incrby(key, score)

        redis_client.expire(key, 86400)

    @classmethod
    async def get_score(

        cls: type,

        chat_id: int
    ) -> int:
        
        if not redis_client:
            logger.warning(
                "Redis client is not initialized",
                extra={
                    "chat_id": chat_id
                }
            )
            return 0

        key = f"{cls.PREFIX}:{chat_id}"

        score = redis_client.get(key)

        return int(score) if score else 0

    @classmethod
    async def reset(

        cls: type,

        chat_id: int
    ) -> None:

        if not redis_client:
            logger.warning(
                "Redis client is not initialized",
                extra={
                    "chat_id": chat_id
                }
            )
            return

        redis_client.delete(

            f"{cls.PREFIX}:{chat_id}"
        )
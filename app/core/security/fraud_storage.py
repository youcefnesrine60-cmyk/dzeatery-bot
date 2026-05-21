#================================
#  تخزين سجل الاحتيال
#================================

from app.core.redis_client import (
    redis_client
)

class FraudStorage:

    PREFIX = "fraud"

    @classmethod
    async def add_score(

        cls: type,

        chat_id: int,

        score: int
    ) -> None:

        key = f"{cls.PREFIX}:{chat_id}"

        redis_client.incrby(key, score)

        redis_client.expire(key, 86400)

    @classmethod
    async def get_score(

        cls: type,

        chat_id: int
    ) -> int:

        key = f"{cls.PREFIX}:{chat_id}"

        score = redis_client.get(key)

        return int(score) if score else 0

    @classmethod
    async def reset(

        cls: type,

        chat_id: int
    ) -> None:

        redis_client.delete(

            f"{cls.PREFIX}:{chat_id}"
        )
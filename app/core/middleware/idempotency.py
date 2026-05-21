#=====================================
#  Idempotency Protection
# هذه مهمة جدًا للـ payments
#=====================================

from app.core.redis_client import (
    redis_client
)


class Idempotency:

    @staticmethod
    async def protect(

        key: str,

        ttl: int = 30
    ) -> bool:

        exists = redis_client.get(key)

        if exists:

            return False

        redis_client.set(
            key,
            "1",
            ex=ttl
        )

        return True
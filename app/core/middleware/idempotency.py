#=====================================
#  Idempotency Protection
# هذه مهمة جدًا للـ payments
#=====================================

from app.core.redis_client import (
    redis_client
)

from app.core.logger import (
    logger
)

class Idempotency:

    @staticmethod
    async def protect(

        key: str,

        ttl: int = 30
    ) -> bool:
        
        if not redis_client:
            logger.warning(
                "Redis client is not initialized",
                extra={
                    "key": key
                }
            )
            return True

        exists = redis_client.get(key)

        if exists:

            logger.warning(
                "idempotency_violation",
                extra={
                    "key": key
                }
            )

            return False

        redis_client.set(
            key,
            "1",
            ex=ttl
        )

        return True
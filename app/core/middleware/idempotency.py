#=====================================
#  Idempotency Protection
# هذه مهمة جدًا للـ payments
#=====================================

from app.core.redis_client import r


class Idempotency:

    @staticmethod
    async def protect(

        key: str,

        ttl: int = 30
    ) -> bool:

        exists = r.get(key)

        if exists:

            return False

        r.set(
            key,
            "1",
            ex=ttl
        )

        return True
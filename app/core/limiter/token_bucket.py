# ==============================================
# 🚦 TOKEN BUCKET LIMITER
# ==============================================

import time

from app.core.redis_client import (
    redis_client,
    memory_storage
)

# ==============================================
# 🚦 TOKEN BUCKET
# ==============================================

class TokenBucket:

    @staticmethod
    async def allow(

        key: str,

        capacity: int = 5,

        refill_rate: float = 1.0

    ) -> bool:

        now = time.time()

        redis_key = f"bucket:{key}"

        # ======================================
        # 🔴 REDIS MODE
        # ======================================

        if redis_client:

            bucket = redis_client.hgetall(redis_key)

            if not bucket:

                tokens = capacity
                last_refill = now

            else:

                tokens = float(bucket["tokens"])
                last_refill = float(bucket["last_refill"])

            # refill
            elapsed = now - last_refill

            tokens = min(

                capacity,

                tokens + elapsed * refill_rate
            )

            if tokens < 1:

                return False

            tokens -= 1

            redis_client.hset(

                redis_key,

                mapping={

                    "tokens": tokens,

                    "last_refill": now
                }
            )

            redis_client.expire(redis_key, 3600)

            return True

        # ======================================
        # 🧠 MEMORY FALLBACK
        # ======================================

        bucket = memory_storage.get(redis_key)

        if not bucket:

            tokens = capacity
            last_refill = now

        else:

            tokens = bucket["tokens"]
            last_refill = bucket["last_refill"]

        # refill
        elapsed = now - last_refill

        tokens = min(

            capacity,

            tokens + elapsed * refill_rate
        )

        if tokens < 1:

            return False

        tokens -= 1

        memory_storage[redis_key] = {

            "tokens": tokens,

            "last_refill": now
        }

        return True
#=============================
#  Burst Protection
#=============================

import time

from app.core.redis_client import (
    redis_client
)


class TokenBucket:

    @staticmethod
    async def allow(

        key: str,

        capacity: int = 20,

        refill_rate: int = 1
    ) -> bool:

        redis_key = f"bucket:{key}"

        now = time.time()

        bucket = redis_client.hgetall(redis_key)

        # =====================================
        # INIT
        # =====================================

        if not bucket:

            redis_client.hset(redis_key, mapping={

                "tokens": capacity,

                "last": now
            })

            redis_client.expire(redis_key, 3600)

            return True

        tokens = float(bucket["tokens"])

        last = float(bucket["last"])

        # =====================================
        # REFILL
        # =====================================

        elapsed = now - last

        refill = elapsed * refill_rate

        tokens = min(

            capacity,

            tokens + refill
        )

        # =====================================
        # BLOCK
        # =====================================

        if tokens < 1:

            return False

        # =====================================
        # CONSUME
        # =====================================

        tokens -= 1

        redis_client.hset(redis_key, mapping={

            "tokens": tokens,

            "last": now
        })

        return True
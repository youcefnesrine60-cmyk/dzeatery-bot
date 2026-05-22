#============================================
# THE SINGLE SOURCE OF TRUTH
# المصدر الوحيد للحقيقة
#============================================

import time

from app.core.redis_client import (
    redis_client
)

from app.core.logger import (
    logger
)

# ==========================================
# 🚫 LUA SLIDING WINDOW LIMITER
# ==========================================

LUA_SCRIPT = """

local key = KEYS[1]

local now = tonumber(ARGV[1])

local window = tonumber(ARGV[2])

local limit = tonumber(ARGV[3])

-- remove old requests
redis.call(
    "ZREMRANGEBYSCORE",
    key,
    0,
    now - window
)

-- count current requests
local count = redis.call(
    "ZCARD",
    key
)

-- block
if count >= limit then
    return 0
end

-- add request
redis.call(
    "ZADD",
    key,
    now,
    tostring(now)
)

-- expire
redis.call(
    "EXPIRE",
    key,
    window
)

return 1
"""


# ==========================================
# 🚫 SLIDING WINDOW LIMITER
# ==========================================

class SlidingWindowLimiter:

    @staticmethod
    async def is_allowed(

        key: str,

        limit: int,

        window: int
    ) -> bool:
        
        if not redis_client:
            logger.warning(
                "Redis client is not initialized",
                extra={
                    "key": key
                }
            )
            return True

        now = time.time()

        redis_key = f"limit:{key}"

        allowed = redis_client.eval(

            LUA_SCRIPT,

            1,

            redis_key,

            now,

            window,

            limit
        )

        return allowed == 1
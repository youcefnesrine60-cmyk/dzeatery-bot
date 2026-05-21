# ==============================================
# 🔴 REDIS CLIENT
# ==============================================

import os

import redis

from app.core.logger import logger

# ==============================================
# 🌍 REDIS URL
# ==============================================

REDIS_URL = os.getenv("REDIS_URL")

# ==============================================
# 🚫 SAFETY CHECK
# ==============================================

if not REDIS_URL:

    raise ValueError(
        "REDIS_URL environment variable is missing."
    )

# ==============================================
# 🔌 CONNECT REDIS
# ==============================================

redis_client = redis.from_url(

    REDIS_URL,

    decode_responses=True
)

logger.info("Redis connected successfully.")
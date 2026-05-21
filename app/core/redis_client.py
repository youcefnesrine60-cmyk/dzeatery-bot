# ==============================================
# 🔴 REDIS CLIENT
# ==============================================

import os
import redis

from dotenv import load_dotenv

from app.core.logger import logger

# ==============================================
# 🌍 LOAD ENV
# ==============================================

load_dotenv()

# ==============================================
# 🌍 REDIS URL
# ==============================================

REDIS_URL = os.getenv("REDIS_URL")

# ==============================================
# 🧠 MEMORY FALLBACK
# ==============================================

memory_storage = {}

# ==============================================
# 🔌 CONNECT REDIS
# ==============================================

if REDIS_URL:

    redis_client = redis.from_url(

        REDIS_URL,

        decode_responses=True
    )

    logger.info(
        "Redis connected successfully."
    )

else:

    redis_client = None

    logger.warning(
        "REDIS_URL not found. Using memory storage."
    )
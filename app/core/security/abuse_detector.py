#=============================
# كشف الاستغلال
#=============================

from app.core.redis_client import r
from app.core.logger import logger


# ==========================================
# 🚫 ABUSE DETECTOR
# ==========================================

class AbuseDetector:

    PREFIX = "abuse"

    LIMIT = 30

    WINDOW = 3600

    # ======================================
    # 🚫 FLAG USER
    # ======================================

    @classmethod
    async def flag(

        cls: type,

        chat_id: int,

        score: int = 1
    ) -> int:

        key = f"{cls.PREFIX}:{chat_id}"

        count = r.incrby(

            key,

            score
        )

        r.expire(

            key,

            cls.WINDOW
        )

        logger.warning(

            "abuse_flagged",

            extra={
                "chat_id": chat_id,
                "score": score,
                "count": count
            }
        )

        return count

    # ======================================
    # 🚫 CHECK ABUSE
    # ======================================

    @classmethod
    async def is_abusive(

        cls: type,

        chat_id: int
    ) -> bool:

        key = f"{cls.PREFIX}:{chat_id}"

        count = r.get(key)

        if not count:

            return False

        abusive = int(count) >= cls.LIMIT

        if abusive:

            logger.warning(

                "abusive_user_detected",

                extra={
                    "chat_id": chat_id,
                    "count": int(count)
                }
            )

        return abusive
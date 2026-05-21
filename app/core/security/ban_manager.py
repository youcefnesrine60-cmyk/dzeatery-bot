#===================================
# bans / suspensions
# الحظر/الإيقاف
#===================================

from app.core.redis_client import (
    redis_client
)
from app.core.logger import (
    logger
)

# ==========================================
# 🚫 BAN MANAGER
# ==========================================

class BanManager:

    PREFIX = "banned"

    # ======================================
    # 🔨 BAN USER
    # ======================================

    @classmethod
    async def ban(

        cls: type,

        chat_id: int,

        ttl: int = 3600
    ) -> None:

        redis_client.setex(

            f"{cls.PREFIX}:{chat_id}",

            ttl,

            "1"
        )

        logger.warning(

            "user_banned",

            extra={
                "chat_id": chat_id,
                "ttl": ttl
            }
        )

    # ======================================
    # ✅ UNBAN USER
    # ======================================

    @classmethod
    async def unban(

        cls: type,

        chat_id: int
    ) -> None:

        redis_client.delete(

            f"{cls.PREFIX}:{chat_id}"
        )

        logger.info(

            "user_unbanned",

            extra={
                "chat_id": chat_id
            }
        )

    # ======================================
    # 🚫 CHECK BAN
    # ======================================

    @classmethod
    async def is_banned(

        cls: type,

        chat_id: int
    ) -> bool:

        banned = redis_client.exists(

            f"{cls.PREFIX}:{chat_id}"

        ) == 1

        if banned:

            logger.warning(

                "banned_user_attempt",

                extra={
                    "chat_id": chat_id
                }
            )

        return banned
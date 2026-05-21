#===========================
# challenge system
# أنظمة التحدي
#===========================

from app.core.redis_client import (
    redis_client
)


class CaptchaManager:

    PREFIX = "captcha"

    ANSWER_PREFIX = "captcha_answer"

    # ==========================================
    # REQUIRE CAPTCHA
    # ==========================================

    @classmethod
    async def require(

        cls: type,

        chat_id: int,

        answer: str
    ) -> None:

        redis_client.setex(

            f"{cls.PREFIX}:{chat_id}",

            300,

            "1"
        )

        redis_client.setex(

            f"{cls.ANSWER_PREFIX}:{chat_id}",

            300,

            answer
        )

    # ==========================================
    # CHECK REQUIRED
    # ==========================================

    @classmethod
    async def is_required(
        cls: type, 
        chat_id: int
    ) -> bool:

        return redis_client.exists(

            f"{cls.PREFIX}:{chat_id}"

        ) == 1

    # ==========================================
    # VERIFY CAPTCHA
    # ==========================================

    @classmethod
    async def verify(

        cls: type,

        chat_id: int,

        user_answer: str
    ) -> bool:

        saved = redis_client.get(

            f"{cls.ANSWER_PREFIX}:{chat_id}"
        )

        return saved == str(user_answer)

    # ==========================================
    # CLEAR
    # ==========================================

    @classmethod
    async def clear(
        cls: type, 
        chat_id: int
    ) -> None:

        redis_client.delete(

            f"{cls.PREFIX}:{chat_id}"
        )

        redis_client.delete(

            f"{cls.ANSWER_PREFIX}:{chat_id}"
        )
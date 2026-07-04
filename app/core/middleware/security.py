from app.core.logger import logger

class SecurityMiddleware:

    BLOCKED_USERS = set()

    @staticmethod
    async def check(
        *,
        chat_id: int
    ) -> bool:

        logger.info(
            "security_check",
            extra={
                "chat_id": chat_id
            }
        )

        return chat_id not in SecurityMiddleware.BLOCKED_USERS
class SecurityMiddleware:

    BLOCKED_USERS = set()

    @staticmethod
    async def check(chat_id: int) -> bool:

        return chat_id not in SecurityMiddleware.BLOCKED_USERS
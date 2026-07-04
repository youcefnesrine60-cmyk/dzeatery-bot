from app.core.logger import logger


# ==========================================
# 📜 REQUEST LOGGER
# ==========================================

class RequestLogger:

    @staticmethod
    async def log(
        *,
        chat_id: int,
        update_type: str
    ) -> None:

        logger.info(
            "request_received",
            extra={
                "chat_id": chat_id,
                "event": update_type,
                "order_id": "-"
            }
        )
from app.services.telegram import (
    send_message,
    edit_message
)

from app.core.logger import (
    logger
)

# ==========================================
# 🎨 UI MANAGER
# ==========================================

class UIManager:

    @staticmethod
    async def update(

        *,

        chat_id: int,

        text: str,

        reply_markup: dict | None = None,

        message_id: int | None = None

    ):

        # ==================================
        # ✏️ EDIT EXISTING MESSAGE
        # ==================================

        if message_id is not None:

            logger.info(

                "editing_existing_message",

                extra={
                    "chat_id": chat_id,
                    "message_id": message_id
                }
            )

            return await edit_message(

                chat_id = chat_id,

                message_id = message_id,

                text = text,

                reply_markup = reply_markup
            )

        # ==================================
        # 💬 SEND NEW MESSAGE
        # ==================================

        logger.info(

            "sending_new_message",

            extra={
                "chat_id": chat_id
            }
        )

        return await send_message(

            chat_id = chat_id,

            text = text,

            reply_markup = reply_markup
        )
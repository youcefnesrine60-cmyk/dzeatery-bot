from app.services.telegram import (
    send_message,
    edit_message
)

from app.core.logger import (
    logger
)

class UIManager:

    @staticmethod
    async def update(

        chat_id,
        text,
        reply_markup=None,
        message_id=None
    ):

        # ==================================
        # EDIT EXISTING MESSAGE
        # ==================================

        if message_id:

            logger.info(
                "editing_existing_message",
                extra={
                    "chat_id": chat_id,
                    "message_id": message_id
                }
            )

            return await edit_message(

                chat_id,
                message_id,
                text,
                reply_markup
            )

        # ==================================
        # SEND NEW MESSAGE
        # ==================================

        logger.info(
            "sending_new_message",
            extra={
                "chat_id": chat_id
            }
        )

        return await send_message(

            chat_id,
            text,
            reply_markup
        )
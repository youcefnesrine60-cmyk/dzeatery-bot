from app.services.telegram_service import (
    send_message,
    edit_message
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

            return await edit_message(

                chat_id,
                message_id,
                text,
                reply_markup
            )

        # ==================================
        # SEND NEW MESSAGE
        # ==================================

        return await send_message(

            chat_id,
            text,
            reply_markup
        )
# ==============================================
# 🎨 UI MANAGER
# ==============================================

from collections.abc import Awaitable

from app.core.logger import logger

from app.services.telegram import (
    edit_message,
    send_message,
)

# ==============================================
# 🏷️ TYPES
# ==============================================

TelegramResponse = dict[str, object] | None
ReplyMarkup = dict[str, object] | None
ReplyMarkupInput = ReplyMarkup | Awaitable[ReplyMarkup]

# ==============================================
# 🎨 UI MANAGER
# ==============================================

class UIManager:

    # ==========================================
    # 📤 SEND OR EDIT MESSAGE
    # ==========================================

    @staticmethod
    async def update(
        *,
        chat_id: int,
        text: str,
        reply_markup: ReplyMarkupInput = None,
        message_id: int | None = None,
    ) -> TelegramResponse:

        # ======================================
        # 🔍 RESOLVE REPLY MARKUP
        # ======================================

        final_reply_markup: ReplyMarkup = None

        if reply_markup is not None:

            if isinstance(reply_markup, Awaitable):

                final_reply_markup = await reply_markup

            else:

                final_reply_markup = reply_markup

            # ==================================
            # 🚫 INVALID REPLY MARKUP
            # ==================================

            if (
                final_reply_markup is not None
                and not isinstance(final_reply_markup, dict)
            ):

                logger.error(
                    "invalid_reply_markup",
                    extra={
                        "chat_id": chat_id,
                        "reply_markup_type": type(
                            final_reply_markup
                        ).__name__,
                    },
                )

                final_reply_markup = None

        # ======================================
        # ✏️ EDIT EXISTING MESSAGE
        # ======================================

        if message_id is not None:

            logger.info(
                "message_edited",
                extra={
                    "chat_id": chat_id,
                    "message_id": message_id,
                },
            )

            return await edit_message(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=final_reply_markup,
            )

        # ======================================
        # 💬 SEND NEW MESSAGE
        # ======================================

        logger.info(
            "message_sent",
            extra={
                "chat_id": chat_id,
            },
        )

        response = await send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=final_reply_markup,
        )

        return response  # ✅ يحتوي على message_id

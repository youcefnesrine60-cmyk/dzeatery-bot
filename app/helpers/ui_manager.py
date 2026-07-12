# ==============================================
# 🎨 UI MANAGER
# ==============================================

from collections.abc import Awaitable

from app.core.logger import logger

# ✅ استيراد دوال المساعدة من state_helper
from app.helpers.state_helper import append_to_state_list

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
        store_message_id: bool = True,
    ) -> TelegramResponse:
        """
        إرسال أو تحديث رسالة، مع تخزين message_id تلقائياً

        Args:
            chat_id: معرف المستخدم
            text: نص الرسالة
            reply_markup: أزرار تفاعلية (اختياري)
            message_id: معرف الرسالة للتعديل (اختياري)
            store_message_id: تخزين message_id في الحالة (افتراضي True)

        Returns:
            TelegramResponse: رد من Telegram
        """
        # ======================================
        # 🔍 RESOLVE REPLY MARKUP
        # ======================================

        final_reply_markup: ReplyMarkup = None

        if reply_markup is not None:
            if isinstance(reply_markup, Awaitable):
                final_reply_markup = await reply_markup
            else:
                final_reply_markup = reply_markup

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

        # ======================================
        # 💾 STORE MESSAGE ID
        # ======================================

        if store_message_id and response and isinstance(response, dict):
            new_message_id = response.get("result", {}).get("message_id")

            if new_message_id:
                # ✅ استخدام الدالة من state_helper
                await append_to_state_list(
                    chat_id=chat_id,
                    list_key="message_ids",
                    value=new_message_id,
                )

        return response
# ==============================================
# 👤 OWNER NAME STEP - VERSION PRO
# ==============================================

from typing import Any

from app.core.logger import logger
from app.helpers.ui_helpers import send_restaurant_name
from app.helpers.safe_sanitize import safe_sanitize
from app.helpers.state_helper import update_state_field, update_state_fields
from app.helpers.state_transition import transition_to
from app.helpers.ui_manager import UIManager
from app.states.owner_states import OwnerStates
from app.views.ui import back_ui

# ==============================================
# 🧩 TYPES
# ==============================================

StateData = dict[str, Any]


# ==============================================
# 👤 HANDLE OWNER NAME STEP
# ==============================================

async def handle_name_step(
    *,
    chat_id: int,
    text: str,
    state: StateData,
    message_id: int,
) -> None:
    """
    معالجة إدخال اسم المالك
    """
    logger.info(
        "handle_name_step",
        extra={
            "chat_id": chat_id,
            "text_length": len(text),
        },
    )

    # ==========================================
    # 🧼 SANITIZE INPUT
    # ==========================================

    clean = safe_sanitize(
        chat_id=chat_id,
        text=text,
        field="owner",
    )

    if clean is None:
        logger.warning(
            "invalid_owner_name",
            extra={
                "chat_id": chat_id,
            },
        )

        # ✅ استخدام bot_message_id من الحالة
        bot_message_id = state.get("bot_message_id")

        if bot_message_id:
            await UIManager.edit(
                chat_id=chat_id,
                message_id=bot_message_id,
                text="❌ الاسم غير صالح. يرجى إدخال اسم صحيح.",
                reply_markup=await back_ui(),
            )
        else:
            await UIManager.send_new_message(
                chat_id=chat_id,
                text="❌ الاسم غير صالح. يرجى إدخال اسم صحيح.",
                reply_markup=await back_ui(),
            )
        return

    # ==========================================
    # 💾 SAVE STATE
    # ==========================================

    await update_state_fields(
        chat_id=chat_id,
        fields={
            "owner": clean,
            "step": OwnerStates.RESTAURANT,
        },
    )

    logger.info(
        "owner_name_saved",
        extra={
            "chat_id": chat_id,
            "owner_name": clean,
        },
    )

    # ==========================================
    # 🔄 TRANSITION TO RESTAURANT STEP
    # ==========================================

    if not await transition_to(
        chat_id=chat_id,
        state=state,
        next_state=OwnerStates.RESTAURANT,
    ):
        logger.error(
            "owner_transition_to_restaurant_failed",
            extra={
                "chat_id": chat_id,
            },
        )
        return

    # ==========================================
    # 🍽️ SEND RESTAURANT NAME SCREEN
    # ==========================================

    # ✅ استخدام bot_message_id من الحالة
    bot_message_id = state.get("bot_message_id")

    if bot_message_id:
        # ✅ تعديل رسالة البوت
        restaurant_message_id = await send_restaurant_name(
            chat_id=chat_id,
            message_id=bot_message_id,
        )
    else:
        # ✅ إرسال رسالة جديدة إذا لم يوجد bot_message_id
        response = await UIManager.send_new_message(
            chat_id=chat_id,
            text="🍽️ أدخل اسم المحل:",
            reply_markup=await back_ui(),
            store_message_id=True,
        )
        restaurant_message_id = None
        if response and isinstance(response, dict):
            restaurant_message_id = response.get("result", {}).get("message_id")

    if restaurant_message_id:
        await update_state_field(
            chat_id=chat_id,
            key="restaurant_message_id",
            value=restaurant_message_id,
        )

        logger.info(
            "restaurant_message_id_saved",
            extra={
                "chat_id": chat_id,
                "restaurant_message_id": restaurant_message_id,
            },
        )
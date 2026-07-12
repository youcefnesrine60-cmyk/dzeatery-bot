# ==============================================
# 🏪 RESTAURANT STEP
# ==============================================

from typing import Any

from app.core.logger import logger

from app.helpers.message import send_wilaya_name
from app.helpers.safe_sanitize import safe_sanitize
from app.helpers.state_helper import update_state_field
from app.helpers.state_transition import transition_to
from app.helpers.ui_manager import UIManager

from app.states.owner_states import OwnerStates

from app.views.ui import back_ui

# ==============================================
# 🧩 TYPES
# ==============================================

StateData = dict[str, Any]


# ==============================================
# 🏪 HANDLE RESTAURANT STEP
# ==============================================

async def handle_restaurant_step(
    *,
    chat_id: int,
    text: str,
    state: StateData,
    message_id: int,
) -> None:
    """
    معالجة إدخال اسم المحل
    """
    logger.info(
        "handle_restaurant_step",
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
        field="restaurant",
    )

    if clean is None:
        logger.warning(
            "invalid_restaurant_name",
            extra={
                "chat_id": chat_id,
            },
        )

        await UIManager.update(
            chat_id=chat_id,
            text="❌ اسم المحل غير صالح. يرجى إدخال اسم صحيح.",
            reply_markup=await back_ui(),
            message_id=message_id,
        )
        return

    # ==========================================
    # 💾 SAVE STATE
    # ==========================================

    state["restaurant"] = clean

    logger.info(
        "restaurant_name_saved",
        extra={
            "chat_id": chat_id,
            "restaurant_name": clean,
        },
    )

    # ==========================================
    # 🔄 TRANSITION TO WILAYA STEP
    # ==========================================

    if not await transition_to(
        chat_id=chat_id,
        state=state,
        next_state=OwnerStates.WILAYA,
    ):
        logger.error(
            "restaurant_transition_to_wilaya_failed",
            extra={
                "chat_id": chat_id,
            },
        )
        return

    # ==========================================
    # 🗺️ SEND WILAYA NAME SCREEN
    # ==========================================

    restaurant_message_id = state.get("restaurant_message_id")

    if restaurant_message_id is None:
        restaurant_message_id = message_id
        logger.warning(
            "restaurant_message_id_not_found_using_user_message_id",
            extra={
                "chat_id": chat_id,
                "message_id": message_id,
            },
        )

    # ✅ إرسال رسالة "أدخل الولاية" (ui_manager يخزن message_id تلقائياً)
    wilaya_message_id = await send_wilaya_name(
        chat_id=chat_id,
        message_id=restaurant_message_id,
    )

    # ✅ فقط نخزن wilaya_message_id في الحالة للاستخدام المستقبلي
    if wilaya_message_id:
        await update_state_field(
            chat_id=chat_id,
            key="wilaya_message_id",
            value=wilaya_message_id,
        )

        logger.info(
            "wilaya_message_id_saved",
            extra={
                "chat_id": chat_id,
                "wilaya_message_id": wilaya_message_id,
            },
        )
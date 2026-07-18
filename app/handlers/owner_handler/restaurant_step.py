# ==============================================
# 🏪 RESTAURANT STEP - VERSION PRO
# ==============================================

from typing import Any

from app.core.logger import logger

from app.helpers.ui_helpers import send_wilaya_name
from app.helpers.safe_sanitize import safe_sanitize
from app.helpers.state_transition import transition_to
from app.helpers.ui_manager import UIManager
from app.helpers.state_helper import (
    update_state_field,
    get_user_state
)

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

    Args:
        chat_id: معرف المستخدم
        text: النص المدخل
        state: حالة المستخدم الحالية
        message_id: معرف رسالة المستخدم (تبقى ظاهرة)
    """
    logger.info(
        "handle_restaurant_step",
        extra={
            "chat_id": chat_id,
            "text_length": len(text),
        },
    )

    # ==========================================
    # 💾 تخزين معرف رسالة المستخدم (لحذفها عند الرجوع)
    # ==========================================

    logger.info(
        "before_storing_user_message_id_restaurant",
        extra={
            "chat_id": chat_id,
            "message_id": message_id,
        },
    )

    #يخزن user_message_id_restaurant في Redis
    await update_state_field(
        chat_id=chat_id,
        key="user_message_id_restaurant",
        value=message_id,
    )

    logger.info(
        "after_storing_user_message_id_restaurant",
        extra={
            "chat_id": chat_id,
            "message_id": message_id,
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

    # ==========================================
    # 🚫 INVALID INPUT
    # ==========================================

    if clean is None:
        logger.warning(
            "invalid_restaurant_name",
            extra={
                "chat_id": chat_id,
            },
        )

        restaurant_message_id = state.get("restaurant_message_id")

        if restaurant_message_id:
            await UIManager.edit(
                chat_id=chat_id,
                message_id=restaurant_message_id,
                text="❌ اسم المحل غير صالح. يرجى إدخال اسم صحيح.",
                reply_markup=await back_ui(),
            )
        else:
            await UIManager.send_new_message(
                chat_id=chat_id,
                text="❌ اسم المحل غير صالح. يرجى إدخال اسم صحيح.",
                reply_markup=await back_ui(),
            )
        return

    # ==========================================
    # 💾 SAVE STATE
    # ==========================================

    await update_state_field(
        chat_id=chat_id,
        key="restaurant",
        value=clean,
    )

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

    # ✅ جلب الحالة المحدثة من Redis
    state = await get_user_state(chat_id=chat_id)

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

    if not restaurant_message_id:
        logger.warning(
            "restaurant_message_id_not_found_using_user_message_id",
            extra={
                "chat_id": chat_id,
                "message_id": message_id,
            },
        )
        restaurant_message_id = message_id

    wilaya_message_id = await send_wilaya_name(
        chat_id=chat_id,
        message_id=restaurant_message_id,
    )

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
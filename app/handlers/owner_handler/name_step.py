# ==============================================
# 👤 OWNER NAME STEP
# ==============================================

from typing import Any

from app.core.logger import logger

from app.helpers.message import send_restaurant_name
from app.helpers.safe_sanitize import safe_sanitize
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

    # ==========================================
    # 🧼 SANITIZE INPUT
    # ... التحقق من صحة الاسم ...
    # ==========================================

    clean = safe_sanitize(
        chat_id=chat_id,
        text=text,
        field="owner",
    )

    # ==========================================
    # ✅ استخدام bot_message_id المحفوظ في الحالة
    # ==========================================

    bot_message_id = state.get("bot_message_id")

    if bot_message_id is None:
        # إذا لم يكن موجوداً، نستخدم message_id الخاص بالمستخدم (كحل احتياطي)
        bot_message_id = message_id
        logger.warning(
            "bot_message_id_not_found_using_user_message_id",
            extra={
                "chat_id": chat_id,
                "message_id": message_id,
            },
        )

    # ==========================================
    # 🚫 INVALID INPUT
    # ==========================================

    if clean is None:

        logger.warning(
            "invalid_owner",
            extra={
                "chat_id": chat_id,
            },
        )

        await UIManager.update(
            chat_id=chat_id,
            text="❌ الاسم غير صالح.",
            reply_markup=await back_ui(),
        )

        return

    # ==========================================
    # 💾 SAVE STATE ( # ... حفظ البيانات  ...)
    # ==========================================

    state["owner"] = clean

    # ==========================================
    # 🔄 TRANSITION (الانتقال)
    # ==========================================

    if not await transition_to(
        chat_id=chat_id,
        state=state,
        next_state=OwnerStates.RESTAURANT,
    ):
        logger.error(
            "owner_transition_failed",
            extra={
                "chat_id": chat_id,
            },
        )
        return
    
    # ==========================================
    # 🍽️ REQUEST RESTAURANT NAME
    # ==========================================

    await send_restaurant_name(
        chat_id=chat_id,
        message_id=bot_message_id,  # ✅ نمرر message_id الخاص بالبوت
    )
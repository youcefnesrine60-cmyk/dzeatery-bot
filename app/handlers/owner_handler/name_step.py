# ==============================================
# 👤 OWNER NAME STEP
# ==============================================

from typing import Any

from app.core.logger import logger

from app.helpers.message import send_restaurant_name
from app.helpers.safe_sanitize import safe_sanitize
from app.helpers.state_transition import transition_to
from app.helpers.ui_manager import UIManager

from app.repositories.state_repo import set_state

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
    # ✅ استخدام owner_name_message_id 
    # المحفوظ في الحالة
    # ==========================================

    owner_name_message_id = state.get("owner_name_message_id")

    if owner_name_message_id is None:
        # إذا لم يكن موجوداً، نستخدم message_id الخاص بالمستخدم (كحل احتياطي)
        owner_name_message_id = message_id
        logger.warning(
            "owner_name_message_id_not_found_using_user_message_id",
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

    # ✅ الحصول على message_id الجديد
    restau_message_id = await send_restaurant_name(
        chat_id=chat_id,
        message_id=owner_name_message_id,
    )

    # ✅ حفظ message_id الجديد في الحالة (للاستخدام المستقبلي)
    if restau_message_id:
        state["restaurant_message_id"] = restau_message_id
        await set_state(
            chat_id=chat_id,
            state={
                "flow": "restaurant",
                "step": OwnerStates.RESTAURANT,
                "history": [],
                "restaurant_message_id": restau_message_id,
            },
        )
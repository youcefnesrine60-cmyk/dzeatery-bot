from app.helpers.safe_sanitize import (
    safe_sanitize
)

from app.helpers.state_transition import (
    transition_to
)

from app.helpers.ui_manager import (
    UIManager
)

from app.views.ui import (
    back_ui,
    location_webapp_ui
)

from app.states.owner_states import (
    OwnerStates
)

from app.core.logger import (
    logger
)


# ==============================================
# 📍 WILAYA STEP
# ==============================================

async def handle_wilaya_step(

    *,

    chat_id: int,

    text: str,

    state: dict

) -> None:

    # ==========================================
    # 🧼 SANITIZE INPUT
    # ==========================================

    clean = safe_sanitize(

        chat_id=chat_id,

        text=text,

        field="wilaya"
    )

    # ==========================================
    # 🚫 INVALID INPUT
    # ==========================================

    if not clean:

        logger.warning(

            "invalid_wilaya",

            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(

            chat_id=chat_id,

            text="❌ ولاية غير صالحة.",

            reply_markup=back_ui()
        )

        return

    # ==========================================
    # 💾 SAVE STATE
    # ==========================================

    state["wilaya"] = clean

    # ==========================================
    # 🔄 TRANSITION
    # ==========================================

    success = await transition_to(

        chat_id=chat_id,

        state=state,

        next_state=OwnerStates.LOCATION
    )

    # ==========================================
    # 🚫 TRANSITION FAILED
    # ==========================================

    if not success:

        logger.error(

            "wilaya_transition_failed",

            extra={
                "chat_id": chat_id
            }
        )

        return

    # ==========================================
    # 📍 ASK LOCATION
    # ==========================================

    await UIManager.update(

        chat_id=chat_id,

        text="📍 اضغط على الزر لتحديد موقع المحل على الخريطة:",

        reply_markup=location_webapp_ui()
    )
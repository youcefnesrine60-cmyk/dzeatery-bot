from app.helpers.safe_sanitize import (
    safe_sanitize
)

from app.helpers.state_transition import (
    transition_to
)

from app.helpers.ui_manager import (
    UIManager
)

from app.helpers.message import (
    send_wilaya_name
)

from app.states.owner_states import (
    OwnerStates
)

from app.core.logger import (
    logger
)

from app.views.ui import (
    back_ui
)


# ==============================================
# 🏪 RESTAURANT STEP
# ==============================================

async def handle_restaurant_step(

    *,

    chat_id: int,

    text: str,

    state: dict

) -> None:

    # ==========================================
    # 🧼 SANITIZE INPUT
    # ==========================================

    clean = safe_sanitize(

        chat_id = chat_id,

        text = text,

        field = "restaurant"
    )

    # ==========================================
    # 🚫 INVALID INPUT
    # ==========================================

    if not clean:

        logger.warning(

            "invalid_restaurant",

            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(

            chat_id = chat_id,

            text = "❌ اسم المحل غير صالح.",

            reply_markup = back_ui()
        )

        return

    # ==========================================
    # 💾 SAVE DATA
    # ==========================================

    state["restaurant"] = clean

    logger.info(

        "restaurant_saved",

        extra={
            "chat_id": chat_id,
            "restaurant": clean
        }
    )

    # ==========================================
    # 🔄 TRANSITION
    # ==========================================

    success = await transition_to(

        chat_id = chat_id,

        state = state,

        next_state = OwnerStates.WILAYA
    )

    # ==========================================
    # 🚫 TRANSITION FAILED
    # ==========================================

    if not success:

        logger.error(

            "transition_to_wilaya_failed",

            extra={
                "chat_id": chat_id
            }
        )

        return

    # ==========================================
    # 🗺️ NEXT SCREEN
    # ==========================================

    logger.info(

        "prompting_for_wilaya",

        extra={
            "chat_id": chat_id
        }
    )

    await send_wilaya_name(

        chat_id = chat_id
    )
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

    chat_id: int,

    text: str,

    state: dict

) -> None:

    clean = safe_sanitize(

        chat_id,

        text,

        "wilaya_name"
    )

    if not clean:

        logger.warning(

            "invalid_wilaya",

            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(

            chat_id,

            "❌ ولاية غير صالحة."
        )

        return

    state["wilaya"] = clean

    success = await transition_to(

        chat_id,

        state,

        OwnerStates.LOCATION
    )

    if not success:
        return

    await UIManager.update(

        chat_id,

        "📍 اضغط على الزر لتحديد موقع المحل على الخريطة:",

        location_webapp_ui()
    )
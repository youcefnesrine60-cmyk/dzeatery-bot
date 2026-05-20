# ==============================================
# 🍽️ CUSTOMER CALLBACK
# 🍽️ SHOW RESTAURANTS
# ==============================================

import re

from app.core.logger import (
    logger
)

from app.repositories.user_repo import (
    has_consent
)

from app.repositories.state_repo import (
    set_state
)

from app.helpers.ui_manager import (
    UIManager
)

from app.views.ui import (
    consent_text,
    consent_ui
)

from app.handlers.customer_handler.restaurant_step import (
    show_restaurants
)

from app.states.customer_states import (
    CustomerStates
)


# ==============================================
# 👤 CUSTOMER CALLBACK
# ==============================================

async def customer_callback(

    chat_id: int,

    message_id: int,

    callback_data: str,

    match: re.Match

) -> None:

    # ==========================================
    # 🚫 CONSENT REQUIRED
    # ==========================================

    if not has_consent(chat_id):

        logger.info(

            "customer_consent_required",

            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(

            chat_id,

            message_id,

            consent_text(),

            consent_ui("customer")
        )

        return

    # ==========================================
    # 🧠 INIT CUSTOMER FLOW
    # ==========================================

    set_state(chat_id, {

        "flow": "customer",

        "step": CustomerStates.RESTAURANT,

        "history": []
    })

    logger.info(

        "customer_flow_started",

        extra={
            "chat_id": chat_id
        }
    )

    # ==========================================
    # 🍽️ SHOW RESTAURANTS
    # ==========================================

    await show_restaurants(

        chat_id,

        message_id
    )
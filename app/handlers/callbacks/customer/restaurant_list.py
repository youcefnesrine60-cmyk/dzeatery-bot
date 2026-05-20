# ==============================================
# 🍽️ CUSTOMER CALLBACK
# 🍽️ SHOW RESTAURANTS
# ==============================================

import re

from app.core.logger import (
    logger
)

from app.repositories.restaurant_repo import (
    get_all_restaurants
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

from app.states.customer_states import (
    CustomerStates
)

from app.views.ui import (
    restaurants_ui
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

    await show_restaurants(
        chat_id,
        message_id
    )

# ==========================================
# 🍽️ SHOW RESTAURANTS
# عرض قائمة المطاعم للمستخدم
# ==========================================

async def show_restaurants(
    chat_id: int,
    message_id: int
) -> None:

    restaurants = get_all_restaurants()

    if not restaurants:

        logger.warning(
            "لا توجد مطاعم لعرضها للمستخدم",
            extra=
            {
                "chat_id": chat_id
            }
        )
        await UIManager.update(
            chat_id,
            message_id,
            "❌ عذراً، قائمة المطاعم غير متوفرة حالياً"
        )

        return

    await UIManager.update(
        chat_id,
        message_id,
        "🍽️ اختر مطعم:",
        restaurants_ui(restaurants)
    )
# ==============================================
# 🍽️ CUSTOMER RESTAURANT LIST
# مسؤول عن عرض قائمة المطاعم
# ==============================================

import re

from app.core.logger import logger

from app.repositories.user_repo import (
    has_consent
)

from app.helpers.ui_manager import (
    UIManager
)

from app.views.ui import (
    consent_text,
    consent_ui
)

from app.handlers.customer_handler import (
    show_restaurants
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
    # 🍽️ SHOW RESTAURANTS
    # ==========================================

    logger.info(

        "customer_restaurants_requested",

        extra={
            "chat_id": chat_id
        }
    )

    await show_restaurants(

        chat_id,

        message_id
    )
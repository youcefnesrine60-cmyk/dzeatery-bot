# ==============================================
# 🏪 OWNER CALLBACKS
# Owner Registration & Consent Flow
# ==============================================

import re

from app.core.logger import logger

from app.helpers.state_helper import update_state_field
from app.helpers.ui_manager import UIManager

from app.repositories.state_repo import (
    delete_state,
    set_state,
)

from app.repositories.user_repo import (
    give_consent,
    has_consent,
)

from app.states.owner_states import OwnerStates

from app.handlers.callbacks.customer.restaurant_list import (
    show_restaurants,
)

from app.views.texts import (
    OWNER_NAME,
)

from app.views.ui import (
    back_ui,
    consent_text,
    consent_ui,
)

# ==============================================
# 👤 OWNER CALLBACK
# ==============================================

async def owner_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match[str],
) -> None:
    """
    معالجة اختيار "صاحب محل" من القائمة الرئيسية
    """
    logger.info(
        "owner_callback_triggered",
        extra={
            "chat_id": chat_id,
            "message_id": message_id,
        },
    )

    # ==========================================
    # 🚫 CONSENT REQUIRED
    # ==========================================

    if not await has_consent(chat_id=chat_id):
        logger.info(
            "owner_consent_required",
            extra={
                "chat_id": chat_id,
            },
        )

        await UIManager.update(
            chat_id=chat_id,
            text=await consent_text(),
            reply_markup=await consent_ui(role="owner"),
            message_id=message_id,
        )
        return

    # ==========================================
    # 🧹 CLEANUP PREVIOUS STATE
    # ==========================================

    await delete_state(chat_id=chat_id)

    # ==========================================
    # 🚀 START OWNER FLOW (مرة واحدة فقط)
    # ==========================================

    await set_state(
        chat_id=chat_id,
        state={
            "flow": "owner",
            "step": OwnerStates.NAME,
            "history": [],
            "bot_message_id": message_id,
        },
    )

    logger.info(
        "owner_flow_started",
        extra={
            "chat_id": chat_id,
        },
    )

    await UIManager.update(
        chat_id=chat_id,
        text=OWNER_NAME,
        reply_markup=await back_ui(),
        message_id=message_id,
    )


# ==============================================
# ✅ CONSENT CALLBACK
# ==============================================

async def consent_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match[str],
) -> None:
    """
    معالجة الموافقة على الشروط
    """
    await give_consent(chat_id=chat_id)

    if callback_data.endswith("owner"):
        logger.info(
            "owner_consent_accepted",
            extra={
                "chat_id": chat_id,
            },
        )

        await delete_state(chat_id=chat_id)

        await set_state(
            chat_id=chat_id,
            state={
                "flow": "owner",
                "step": OwnerStates.NAME,
                "history": [],
                "bot_message_id": message_id,
            },
        )

        await UIManager.update(
            chat_id=chat_id,
            text=OWNER_NAME,
            reply_markup=await back_ui(),
            message_id=message_id,
        )
        return

    logger.info(
        "customer_consent_accepted",
        extra={
            "chat_id": chat_id,
        },
    )

    await show_restaurants(
        chat_id=chat_id,
        message_id=message_id,
    )
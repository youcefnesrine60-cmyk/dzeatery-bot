# ==============================================
# 🏪 OWNER (صاحب المحل)
# owner_callback - consent_callback
# This file contains the callbacks related to 
# the owner registration process.
# ==============================================
import re

from app.repositories.user_repo import has_consent
from app.helpers.ui_manager import UIManager
from app.repositories.state_repo import set_state
from app.repositories.user_repo import give_consent
from app.states.owner_states import OwnerStates
from app.views.texts import OWNER_NAME
from app.handlers.callbacks.customer.restaurant_list import show_restaurants
from app.core.logger import logger
from app.views.ui import *

# ==============================================
# 👤 OWNER CALLBACK
# ==============================================

async def owner_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match,
) -> None:
    """
    معالجة اختيار "صاحب محل" من القائمة الرئيسية
    """
    logger.info(
        "owner_callback_triggered",
        extra={
            "chat_id": chat_id,
        },
    )

    # التحقق من الموافقة على الشروط
    if not await has_consent(chat_id=chat_id):
        logger.info(
            "owner_no_consent",
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

    # بدء تدفق المالك
    await set_state(
        chat_id=chat_id,
        state={
            "flow": "owner",
            "step": OwnerStates.NAME,
            "history": [],
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
# ✅ CONSENT
# ==============================================

async def consent_callback(
    *,
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    await give_consent(
        chat_id = chat_id)

    if callback_data.endswith("owner"):

        logger.info(
            "owner_given_consent",
             extra={
                "chat_id": chat_id
            }
        )

        await set_state(
            chat_id = chat_id, 
            state = {
                "flow": "owner",
                "step": OwnerStates.NAME,
                "history": []
            }
        )

        logger.info(
            "owner_flow_started_after_consent",
            extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(
            chat_id = chat_id,
            text = OWNER_NAME,
            reply_markup = await back_ui(),
            message_id = message_id
        )

    else:

        logger.info(
            "customer_given_consent",
            extra={
                "chat_id": chat_id
            }
        )

        await show_restaurants(
            chat_id = chat_id,
            message_id = message_id
        )

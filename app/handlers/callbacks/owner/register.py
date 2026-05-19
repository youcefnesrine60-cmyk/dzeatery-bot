# ==============================================
# 🏪 OWNER (صاحب المحل)
# This file contains the callbacks related to 
# the owner registration process.
# ==============================================
import re

from app.repositories.user_repo import (
    has_consent
)

from app.helpers.ui_manager import (
    UIManager
)

from app.repositories.state_repo import (
    set_state
)

from app.repositories.user_repo import (
    give_consent
)

from app.states.owner_states import (
    OwnerStates
)

from app.views.texts import (
     OWNER_NAME
)

from app.handlers.customer_handler import (
    show_restaurants
)

from app.core.logger import (
    logger
)

from app.views.ui import *


# ==============================================
# 👤 OWNER
# ==============================================

async def owner_callback(
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    if not has_consent(chat_id):
            
            logger.info(
                 
                "OWNER has not given consent, showing consent screen",

                 extra={
                    "chat_id": chat_id
                }
                 
            )

            await UIManager.update(
                chat_id,
                message_id,

                consent_text(),

                consent_ui("owner")
            )

            return
    
    logger.info(
                
            "User {chat_id} has given consent",
            
            extra={
                "chat_id": chat_id
            }
    )

    set_state(chat_id, {
         
        "flow": "owner",

        "step": OwnerStates.NAME,

        "history": []
    })

    logger.info(
         
        "User {chat_id} is proceeding to the name step",
        
        extra={
            "chat_id": chat_id
        }
    )

    await UIManager.update(

        chat_id,

        message_id,

        OWNER_NAME,

        back_ui()
    )


# ==============================================
# ✅ CONSENT
# ==============================================

async def consent_callback(
    chat_id: int,
    message_id: int,
    callback_data: str,
    match: re.Match
) -> None:

    give_consent(chat_id)

    if callback_data.endswith("owner"):

        set_state(chat_id, {
             
            "flow": "owner",

            "step": OwnerStates.NAME,

            "history": []
        })

        logger.info(
             
             "User {chat_id} is proceeding to the name step",
             
             extra={
                "chat_id": chat_id
            }
        )

        await UIManager.update(

            chat_id,

            message_id,

            OWNER_NAME,

            back_ui()
        )

    else:

        logger.info(
            "User {chat_id} is proceeding to the restaurants list",
            extra={
                "chat_id": chat_id
            }
        )

        await show_restaurants(
            chat_id,
            message_id
        )

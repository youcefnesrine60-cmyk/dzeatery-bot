# ==============================================
# 🍽️ TYPE CALLBACK
# ==============================================

import re

from app.helpers.ui_manager import (
    UIManager
)

from app.repositories.state_repo import (
    get_state,
    set_state
)

from app.states.owner_states import (
    OwnerStates
)

from app.views.texts import (
    PHONE_NUMBER
)

from app.views.ui import (
    back_ui
)

from app.core.logger import (
    logger
)

# ==============================================
# 🍽️ TYPE
# ==============================================

async def type_callback(

    *,

    chat_id: int,

    message_id: int,

    callback_data: str,

    match: re.Match

) -> None:

    # ==========================================
    # 📥 LOAD STATE
    # ==========================================

    state = get_state(

        chat_id = chat_id
    )

    # ==========================================
    # 🚫 STATE NOT FOUND
    # ==========================================

    if not state:

        logger.warning(

            "type_state_missing",

            extra={
                "chat_id": chat_id
            }
        )

        return

    try:

        # ======================================
        # 🍽️ SAVE TYPE
        # ======================================

        selected_type = callback_data.replace(

            "type_",
            ""
        )

        state["type"] = selected_type

        # ======================================
        # 📜 UPDATE HISTORY
        # ======================================

        state["history"].append(

            OwnerStates.TYPE
        )

        # ======================================
        # 🔄 UPDATE STEP
        # ======================================

        state["step"] = OwnerStates.PHONE

        # ======================================
        # 💾 SAVE STATE
        # ======================================

        set_state(

            chat_id = chat_id,

            state = state
        )

        logger.info(

            "type_selected_successfully",

            extra={

                "chat_id": chat_id,

                "type": selected_type,

                "next_step": OwnerStates.PHONE
            }
        )

        # ======================================
        # 📞 ASK PHONE
        # ======================================

        await UIManager.update(

            chat_id = chat_id,

            text = PHONE_NUMBER,

            reply_markup = back_ui(),

            message_id = message_id
        )

    except Exception as e:

        logger.exception(

            "type_callback_failed",

            extra={

                "chat_id": chat_id,

                "error": str(e)
            }
        )
# ==============================================
# 🔙 NAVIGATION HELPER
# ==============================================

from app.repositories.state_repo import (
    get_state,
    set_state
)

from app.core.logger import (
    logger
)

from app.states.owner_states import (
    OwnerStates
)

# ==============================================
# 🧹 STEP CLEANUP MAP
# تنظيف البيانات حسب المرحلة
# ==============================================

STEP_CLEANUP = {

    OwnerStates.NAME: [

        "owner",
        "restaurant",
        "wilaya",
        "lat",
        "lng",
        "type",
        "phone"
    ],

    OwnerStates.RESTAURANT_NAME: [

        "restaurant",
        "wilaya",
        "lat",
        "lng",
        "type",
        "phone"
    ],

    OwnerStates.WILAYA: [

        "wilaya",
        "lat",
        "lng",
        "type",
        "phone"
    ],

    OwnerStates.LOCATION: [

        "lat",
        "lng",
        "type",
        "phone"
    ],

    OwnerStates.TYPE: [

        "type",
        "phone"
    ],

    OwnerStates.PHONE: [

        "phone"
    ]
}

# ==============================================
# 🔙 GO BACK
# ==============================================

def go_back(

    chat_id: int

) -> str | None:

    state = get_state(chat_id)

    # ==========================================
    # 🚫 NO STATE
    # ==========================================

    if not state:

        logger.warning(

            "navigation_state_missing",

            extra={
                "chat_id": chat_id
            }
        )

        return None

    history = state.get("history", [])

    # ==========================================
    # 🚫 EMPTY HISTORY
    # ==========================================

    if not history:

        logger.info(

            "navigation_history_empty",

            extra={
                "chat_id": chat_id
            }
        )

        return None

    # ==========================================
    # 🔙 GET PREVIOUS STEP
    # ==========================================

    previous_step = history.pop()

    # ==========================================
    # 🧹 CLEAN RELATED DATA
    # ==========================================

    for key in STEP_CLEANUP.get(previous_step, []):

        state.pop(key, None)

    # ==========================================
    # 💾 UPDATE STATE
    # ==========================================

    state["step"] = previous_step

    set_state(chat_id, state)

    logger.info(

        "navigation_back_success",

        extra={
            "chat_id": chat_id,
            "step": previous_step
        }
    )

    return previous_step
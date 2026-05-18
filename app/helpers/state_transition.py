from app.repositories.state_repo import (
    set_state
)

from app.helpers.state_machine import (
    can_transition
)

from app.core.logger import (
    logger
)


# ==============================================
# 🔄 STATE TRANSITION HELPER
# ==============================================

async def transition_to(

    chat_id: int,

    state: dict,

    next_state: str

) -> bool:

    current = state["step"]

    # ==========================================
    # 🚫 INVALID TRANSITION
    # ==========================================

    if not can_transition(

        current,

        next_state
    ):

        logger.warning(

            "invalid_state_transition",

            extra={

                "chat_id": chat_id,

                "from": current,

                "to": next_state
            }
        )

        return False

    # ==========================================
    # 📚 SAVE HISTORY
    # ==========================================

    state["history"].append(current)

    # ==========================================
    # 🔄 UPDATE STEP
    # ==========================================

    state["step"] = next_state

    # ==========================================
    # 💾 SAVE STATE
    # ==========================================

    set_state(

        chat_id,

        state
    )

    logger.info(

        "state_transition_success",

        extra={

            "chat_id": chat_id,

            "from": current,

            "to": next_state
        }
    )

    return True
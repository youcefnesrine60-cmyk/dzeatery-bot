# ==============================================
# 🧠 STATE MACHINE
# ==============================================

from app.states.transitions import (
    ALLOWED_TRANSITIONS
)

from app.core.logger import (
    logger
)

# ==============================================
# ✅ CHECK STATE TRANSITION
# ==============================================

def can_transition(

    *,

    current_state: str,

    next_state: str

) -> bool:

    # ==========================================
    # 📚 GET ALLOWED STATES
    # ==========================================

    allowed = ALLOWED_TRANSITIONS.get(

        current_state,

        []
    )

    # ==========================================
    # 🔍 CHECK TRANSITION
    # ==========================================

    is_allowed = next_state in allowed

    # ==========================================
    # 📝 LOG RESULT
    # ==========================================

    logger.info(

        "state_transition_checked",

        extra={

            "from": current_state,

            "to": next_state,

            "allowed": is_allowed
        }
    )

    return is_allowed
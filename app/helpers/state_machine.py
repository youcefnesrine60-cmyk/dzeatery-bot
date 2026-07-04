# ==============================================
# 🧠 STATE MACHINE
# ==============================================

from app.states.transitions import ALLOWED_TRANSITIONS

# ==============================================
# ✅ CHECK STATE TRANSITION
# ==============================================

async def can_transition(
    *,
    current_state: str,
    next_state: str,
) -> bool:

    # ==========================================
    # 📚 GET ALLOWED TRANSITIONS
    # ==========================================

    allowed = ALLOWED_TRANSITIONS.get(
        current_state,
        (),
    )

    # ==========================================
    # ✅ CHECK TRANSITION
    # ==========================================

    return next_state in allowed
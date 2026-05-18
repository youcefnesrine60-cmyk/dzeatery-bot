from app.states.transitions import (
    ALLOWED_TRANSITIONS
)


def can_transition(
    current_state,
    next_state
):

    allowed = ALLOWED_TRANSITIONS.get(
        current_state,
        []
    )

    return next_state in allowed
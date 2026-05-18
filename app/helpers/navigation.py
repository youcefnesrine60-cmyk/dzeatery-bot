from app.repositories.state_repo import (
    get_state,
    set_state
)

# =====================================================
# 🔙 BACK SYSTEM
# =====================================================

def go_back(

    chat_id: int

) -> str | None:

    state = get_state(chat_id)

    if not state:
        return None

    if not state.get("history"):
        return None

    previous_step = state["history"].pop()

    # تنظيف البيانات حسب المرحلة
    cleanup = {

        "name": [
            "owner",
            "restaurant",
            "wilaya",
            "lat",
            "lng",
            "type",
            "phone"
        ],

        "restaurant_name": [
            "restaurant",
            "wilaya",
            "lat",
            "lng",
            "type",
            "phone"
        ],

        "wilaya": [
            "wilaya",
            "lat",
            "lng",
            "type",
            "phone"
        ],

        "location": [
            "lat",
            "lng",
            "type",
            "phone"
        ],

        "type": [
            "type",
            "phone"
        ],

        "phone": [
            "phone"
        ]
    }

    for key in cleanup.get(previous_step, []):

        state.pop(key, None)

    state["step"] = previous_step

    set_state(chat_id, state)

    return previous_step
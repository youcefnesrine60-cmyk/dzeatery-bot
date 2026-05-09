from app.repositories.state_repo import (
    get_state,
    set_state
)

# =====================================================
# 🔙 BACK SYSTEM
# =====================================================

def go_back(chat_id):
    state = get_state(chat_id)

    if not state or not state.get("history"):
        return None

    previous_step = state["history"].pop()

    # تنظيف البيانات حسب المرحلة
    cleanup = {
        "name": ["owner", "restaurant", "wilaya", "lat", "lng", "type", "phone"],
        "restaurant_name": ["restaurant", "wilaya", "lat", "lng", "type", "phone"],
        "wilaya": ["wilaya", "lat", "lng", "type", "phone"],
        "location": ["lat", "lng", "type", "phone"],
        "type": ["type", "phone"],
        "phone": ["phone"],
    }

    for k in cleanup.get(previous_step, []):
        state.pop(k, None)

    state["step"] = previous_step
    set_state(chat_id, state)
    return previous_step
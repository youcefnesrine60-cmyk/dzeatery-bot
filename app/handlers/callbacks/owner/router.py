#=================================================
# OWNER CALLBACK ROUTES
# هذا الملف مسؤول فقط عن تسجيل routes 
# الخاصة بالمالك، وليس عن تنفيذ المنطق الخاص بها.
#=================================================


from app.core.router_instance import router

from app.handlers.callbacks.owner.register import (
    owner_callback,
    consent_callback
)

from app.handlers.callbacks.owner.confirm import (
    confirm_callback
)

from app.handlers.callbacks.owner.navigation import (
    back_main_callback,
    back_step_callback,
    decline_callback
)


# ==========================================
# REGISTER OWNER ROUTES
# ==========================================

def register_owner_routes() -> None:

    # ============================================
    # OWNER ROUTES
    # ============================================

    router.register(
        r"^owner$",
        owner_callback
    )

    # ============================================
    # CONSENT & CONFIRMATION
    # ============================================

    router.register(
        r"^consent_.*",
        consent_callback
    )

    router.register(
        r"^confirm$",
        confirm_callback
    )

    # ============================================
    # NAVIGATION
    # ============================================

    router.register(
        r"^back_main$",
        back_main_callback
    )

    router.register(
        r"^back_step$",
        back_step_callback
    )

    router.register(
        r"^decline$",
        decline_callback
    )
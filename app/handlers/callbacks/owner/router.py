# =================================================
# 👤 OWNER CALLBACK ROUTES
# هذا الملف مسؤول فقط عن تسجيل Routes
# الخاصة بالمالك، وليس عن تنفيذ المنطق الخاص بها
# =================================================

from app.core.logger import logger
from app.core.router_instance import router
from app.handlers.callbacks.owner.confirm import confirm_callback
from app.handlers.callbacks.owner.register import (
    owner_callback,
    consent_callback,
)
from app.handlers.callbacks.owner.navigation import (
    back_main_callback,
    back_step_callback,
    decline_callback,
)

# =================================================
# 🚀 REGISTER OWNER ROUTES
# =================================================

async def register_owner_routes() -> None:

    # ==========================================
    # 👤 OWNER ROUTES
    # ==========================================

    router.register(
        pattern=r"^owner$",
        handler=owner_callback,
    )

    # ==========================================
    # ✅ CONSENT & CONFIRMATION
    # ==========================================

    router.register(
        pattern=r"^consent_.*$",
        handler=consent_callback,
    )

    router.register(
        pattern=r"^confirm$",
        handler=confirm_callback,
    )

    # ==========================================
    # 🔙 NAVIGATION
    # ==========================================

    router.register(
        pattern=r"^back_main$",
        handler=back_main_callback,
    )

    router.register(
        pattern=r"^back_step$",
        handler=back_step_callback,
    )

    router.register(
        pattern=r"^decline$",
        handler=decline_callback,
    )

    logger.info(
        "owner_callback_routes_registered",
    )
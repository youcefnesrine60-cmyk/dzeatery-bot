# ==============================================
# 🚀 DZ-EATERY MAIN APPLICATION
# ==============================================

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.webhook import router
from app.api.webhook import register_routes  # ✅ استيراد دالة التسجيل
from app.core.db import init_db, close_db
from app.core.logger import logger


# ==============================================
# 🚀 LIFESPAN MANAGER
# ==============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    إدارة دورة حياة التطبيق
    - بدء التشغيل: تهيئة قاعدة البيانات وتسجيل المسارات
    - الإغلاق: إغلاق اتصال قاعدة البيانات
    """
    # ==========================================
    # 🚀 STARTUP
    # ==========================================

    logger.info(
        "application_starting",
    )

    # تهيئة قاعدة البيانات
    await init_db()

    # تسجيل مسارات الكولباك
    await register_routes()

    logger.info(
        "application_started",
    )

    yield

    # ==========================================
    # 🛑 SHUTDOWN
    # ==========================================

    logger.info(
        "application_shutting_down",
    )

    # إغلاق اتصال قاعدة البيانات
    await close_db()

    logger.info(
        "application_shutdown_complete",
    )


# ==============================================
# 🚀 CREATE FASTAPI APPLICATION
# ==============================================

app = FastAPI(
    title="DZ Eatery Bot",
    version="1.0.0",
    lifespan=lifespan,
)

# ==============================================
# 📌 INCLUDE ROUTERS
# ==============================================

app.include_router(router)
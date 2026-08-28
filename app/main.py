# ==============================================
# 🚀 DZ-EATERY MAIN APPLICATION
# ==============================================
"""التطبيق الرئيسي لمنصة DZ-Eatery."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.registration_request import router as registration_requests_router
from app.api.v1.restaurants import router as restaurants_router
from app.api.v1.owners import router as owners_router
from app.api.v1.payments import router as payments_router
from app.api.v1.products import router as products_router
from app.api.v1.branches import router as branches_router
from app.api.v1.categories import router as categories_router
from app.api.v1.orders import router as orders_router
from app.api.v1.order_item import router as order_items_router
from app.api.v1.restaurant_payment_setting import router as payment_settings_router
from app.api.v1.restaurant_metric import router as restaurant_metrics_router
from app.api.v1.restaurant_order_counter import router as order_counter_router
from app.api.v1.option_group import router as option_groups_router
from app.api.v1.product_option import router as product_options_router
from app.api.v1.user import router as users_router
from app.api.webhook import router as webhook_router
from app.api.webhook import register_routes
from app.core.config import settings
from app.core.db import init_db, close_db
from app.core.logger import logger


# ==============================================
# 🚀 LIFESPAN MANAGER
# ==============================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    إدارة دورة حياة التطبيق.
    
    - بدء التشغيل: تهيئة قاعدة البيانات وتسجيل المسارات
    - الإغلاق: إغلاق اتصال قاعدة البيانات
    
    Yields:
        None: يستمر التطبيق في العمل
    """
    # ==========================================
    # 🚀 STARTUP
    # ==========================================

    logger.info(
        "application_starting",
        extra={
            "environment": settings.APP_ENV,
            "debug": settings.DEBUG,
        },
    )

    # تهيئة قاعدة البيانات
    await init_db()

    # تسجيل مسارات الكولباك
    await register_routes()

    logger.info(
        "application_started",
        extra={
            "docs_url": "/docs",
            "redoc_url": "/redoc",
        },
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
    description="🤖 AI Agent Platform for Restaurants",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ==============================================
# 🌐 CORS MIDDLEWARE
# ==============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================
# 📋 INCLUDE ROUTERS
# ==============================================

# ✅ نقاط نهاية المطاعم (API v1)
app.include_router(
    restaurants_router,
    prefix="/api/v1",
    tags=["Restaurants"],
)

# ✅ نقاط نهاية المالكين (API v1)
app.include_router(
    owners_router,
    prefix="/api/v1",
    tags=["Owners"],
)

# ✅ نقاط نهاية طلبات التسجيل (API v1) 
app.include_router(
    registration_requests_router,
    prefix="/api/v1",
    tags=["Registration Requests"],
)

# ✅ نقاط نهاية المدفوعات (API v1)
app.include_router(
    payments_router,
    prefix="/api/v1",
    tags=["Payments"],
)

# ✅ نقاط نهاية المنتجات (API v1)
app.include_router(
    products_router,
    prefix="/api/v1",
    tags=["Products"],
)

# ✅ نقاط نهاية الفروع (API v1)
app.include_router(
    branches_router,
    prefix="/api/v1",
    tags=["Branches"],
)

# ✅ نقاط نهاية التصنيفات (API v1)
app.include_router(
    categories_router,
    prefix="/api/v1",
    tags=["Categories"],
)

# ✅ نقاط نهاية الطلبات (API v1)
app.include_router(
    orders_router,
    prefix="/api/v1",
    tags=["Orders"],
)

# ✅ نقاط نهاية تفاصيل الطلب (API v1)
app.include_router(
    order_items_router,
    prefix="/api/v1",
    tags=["Order Items"],
)

# ✅ نقاط نهاية إعدادات الدفع (API v1)
app.include_router(
    payment_settings_router,
    prefix="/api/v1",
    tags=["Payment Settings"],
)

# ✅ نقاط نهاية مقاييس المطعم (API v1)
app.include_router(
    restaurant_metrics_router,
    prefix="/api/v1",
    tags=["Restaurant Metrics"],
)

# ✅ نقاط نهاية عداد طلبات المطعم (API v1)
app.include_router(
    order_counter_router,
    prefix="/api/v1",
    tags=["Order Counters"],
)

# ✅ نقاط نهاية مجموعات الخيارات (API v1)
app.include_router(
    option_groups_router,
    prefix="/api/v1",
    tags=["Option Groups"],
)

# ✅ نقاط نهاية خيارات المنتج (API v1)
app.include_router(
    product_options_router,
    prefix="/api/v1",
    tags=["Product Options"],
)

# ✅ نقاط نهاية المستخدمين (API v1)
app.include_router(
    users_router,
    prefix="/api/v1",
    tags=["Users"],
)

# ✅ Webhook (Telegram)
app.include_router(
    webhook_router,
    tags=["Webhook"],
)


# ==============================================
# 🏠 ROOT ENDPOINT
# ==============================================

@app.get("/")
async def root() -> dict:
    """
    الصفحة الرئيسية للتطبيق.
    
    Returns:
        dict: معلومات عن التطبيق
    """
    return {
        "message": "Welcome to MoulAI API",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# ==============================================
# ❤️ HEALTH CHECK
# ==============================================

@app.get("/health")
async def health_check() -> dict:
    """
    التحقق من صحة التطبيق.
    
    Returns:
        dict: حالة التطبيق
    """
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "version": "1.0.0",
    }
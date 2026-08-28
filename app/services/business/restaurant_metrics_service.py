# ==============================================
# 📊 RESTAURANT METRICS SERVICE
# منطق الأعمال لمقاييس المطعم
#
# تهيئة المقاييس
# تحديث المقاييس عند إنشاء/حذف منتج
# تحديث المقاييس عند إنشاء/حذف تصنيف
# تحديث المقاييس عند تسجيل طلب
# جلب المقاييس
# ==============================================

from typing import (
    Any,
    Dict,
    Optional,
)

from sqlalchemy.ext.asyncio import AsyncSession

# ✅ استيراد الاستثناءات
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
)

# ✅ استيراد دوال الأمان
from app.core.security import (
    sanitize_input,
)

from app.core.logger import logger
from app.repositories.restaurant_metrics_repo import RestaurantMetricsRepository

# ✅ استيراد المخططات
from app.schemas.restaurant_metric import (
    RestaurantMetricResponse,
    RestaurantMetricUpdate,
    RestaurantMetricSummary,
)


# ==============================================
# 🧩 TYPES
# ==============================================

MetricsDict = Dict[str, Any]


# ==============================================
# 📊 RESTAURANT METRICS SERVICE
# ==============================================


class RestaurantMetricsService:
    """
    خدمة مقاييس المطعم - تدير منطق الأعمال لمقاييس المطاعم.
    
    مسؤولة عن:
        - تهيئة مقاييس المطعم الجديد
        - تحديث المقاييس عند إنشاء/حذف منتج
        - تحديث المقاييس عند إنشاء/حذف تصنيف
        - تحديث المقاييس عند تسجيل طلب
        - جلب المقاييس
    
    Attributes:
        session: جلسة قاعدة البيانات غير المتزامنة
        repo: مستودع مقاييس المطعم
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        تهيئة خدمة مقاييس المطعم.
        
        Args:
            session: جلسة قاعدة البيانات غير المتزامنة
        """
        self.session = session
        self.repo = RestaurantMetricsRepository(session)

    # ==========================================
    # 📖 QUERIES
    # ==========================================

    # ==============================================
    # GET METRICS
    # ==============================================

    async def get_metrics(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantMetricResponse:
        """
        الحصول على مقاييس مطعم معين.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantMetricResponse: بيانات المقاييس
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المقاييس
        """
        logger.info(
            "metrics_service_get_metrics",
            extra={"restaurant_id": restaurant_id},
        )

        metrics = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not metrics:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        return RestaurantMetricResponse.model_validate(metrics)

    # ==============================================
    # GET METRICS DICT
    # ==============================================

    async def get_metrics_dict(
        self,
        *,
        restaurant_id: int,
    ) -> Optional[MetricsDict]:
        """
        الحصول على مقاييس مطعم معين كقاموس.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            Optional[MetricsDict]: قاموس مقاييس المطعم أو None
        """
        logger.info(
            "metrics_service_get_metrics_dict",
            extra={"restaurant_id": restaurant_id},
        )

        metrics = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not metrics:
            return None

        return {
            "restaurant_id": metrics.restaurant_id,
            "products_count": metrics.products_count,
            "categories_count": metrics.categories_count,
            "monthly_orders": metrics.monthly_orders,
            "average_order_value": metrics.average_order_value,
            "created_at": metrics.created_at,
            "updated_at": metrics.updated_at,
        }

    # ==========================================
    # 📊 STATISTICS
    # ==========================================

    # ==============================================
    # GET AVERAGE ORDER VALUE
    # ==============================================

    async def get_average_order_value(
        self,
        *,
        restaurant_id: int,
    ) -> float:
        """
        الحصول على متوسط قيمة الطلب.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            float: متوسط قيمة الطلب
        """
        logger.info(
            "metrics_service_get_average_order_value",
            extra={"restaurant_id": restaurant_id},
        )

        return await self.repo.get_average_order_value(
            restaurant_id=restaurant_id,
        )

    # ==============================================
    # GET MONTHLY ORDERS
    # ==============================================

    async def get_monthly_orders(
        self,
        *,
        restaurant_id: int,
    ) -> int:
        """
        الحصول على عدد الطلبات الشهرية.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            int: عدد الطلبات الشهرية
        """
        logger.info(
            "metrics_service_get_monthly_orders",
            extra={"restaurant_id": restaurant_id},
        )

        return await self.repo.get_monthly_orders(
            restaurant_id=restaurant_id,
        )

    # ==============================================
    # GET TOTAL PRODUCTS
    # ==============================================

    async def get_total_products(
        self,
        *,
        restaurant_id: int,
    ) -> int:
        """
        الحصول على عدد المنتجات.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            int: عدد المنتجات
        """
        logger.info(
            "metrics_service_get_total_products",
            extra={"restaurant_id": restaurant_id},
        )

        return await self.repo.get_total_products(
            restaurant_id=restaurant_id,
        )

    # ==============================================
    # GET TOTAL CATEGORIES
    # ==============================================

    async def get_total_categories(
        self,
        *,
        restaurant_id: int,
    ) -> int:
        """
        الحصول على عدد التصنيفات.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            int: عدد التصنيفات
        """
        logger.info(
            "metrics_service_get_total_categories",
            extra={"restaurant_id": restaurant_id},
        )

        return await self.repo.get_total_categories(
            restaurant_id=restaurant_id,
        )

    # ==============================================
    # GET METRICS SUMMARY
    # ==============================================

    async def get_metrics_summary(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantMetricSummary:
        """
        الحصول على ملخص مقاييس المطعم.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantMetricSummary: ملخص المقاييس
        """
        logger.info(
            "metrics_service_get_metrics_summary",
            extra={"restaurant_id": restaurant_id},
        )

        metrics = await self.get_metrics(
            restaurant_id=restaurant_id,
        )

        return RestaurantMetricSummary(
            restaurant_id=metrics.restaurant_id,
            products_count=metrics.products_count,
            categories_count=metrics.categories_count,
            monthly_orders=metrics.monthly_orders,
            average_order_value=metrics.average_order_value,
        )

    # ==========================================
    # ✏️ MUTATIONS
    # ==========================================

    # ==============================================
    # INITIALIZE METRICS
    # ==============================================

    async def initialize_metrics(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantMetricResponse:
        """
        تهيئة مقاييس مطعم جديد.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantMetricResponse: بيانات المقاييس المنشأة
            
        Raises:
            ValidationError: إذا كانت المقاييس موجودة مسبقاً
        """
        logger.info(
            "metrics_service_initialize",
            extra={"restaurant_id": restaurant_id},
        )

        # التحقق من عدم وجود مقاييس مسبقاً
        existing = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if existing:
            raise ValidationError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' موجودة مسبقاً",
            )

        metrics = await self.repo.create_default(
            restaurant_id=restaurant_id,
        )

        logger.info(
            "metrics_initialized_successfully",
            extra={"restaurant_id": restaurant_id},
        )

        return RestaurantMetricResponse.model_validate(metrics)

    # ==============================================
    # PRODUCT CREATED
    # ==============================================

    async def product_created(
        self,
        *,
        restaurant_id: int,
        amount: int = 1,
    ) -> RestaurantMetricResponse:
        """
        تحديث المقاييس عند إنشاء منتج جديد.
        
        Args:
            restaurant_id: معرف المطعم
            amount: عدد المنتجات المضافة
            
        Returns:
            RestaurantMetricResponse: بيانات المقاييس المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المقاييس
        """
        if amount <= 0:
            raise ValidationError(
                message="العدد يجب أن يكون أكبر من الصفر",
            )

        logger.info(
            "metrics_service_product_created",
            extra={
                "restaurant_id": restaurant_id,
                "amount": amount,
            },
        )

        metrics = await self.repo.increment_products_count(
            restaurant_id=restaurant_id,
            amount=amount,
        )

        if not metrics:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "metrics_product_created_updated",
            extra={
                "restaurant_id": restaurant_id,
                "products_count": metrics.products_count,
            },
        )

        return RestaurantMetricResponse.model_validate(metrics)

    # ==============================================
    # PRODUCT DELETED
    # ==============================================

    async def product_deleted(
        self,
        *,
        restaurant_id: int,
        amount: int = 1,
    ) -> RestaurantMetricResponse:
        """
        تحديث المقاييس عند حذف منتج.
        
        Args:
            restaurant_id: معرف المطعم
            amount: عدد المنتجات المحذوفة
            
        Returns:
            RestaurantMetricResponse: بيانات المقاييس المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المقاييس
            ValidationError: إذا كان العدد غير صالح
        """
        if amount <= 0:
            raise ValidationError(
                message="العدد يجب أن يكون أكبر من الصفر",
            )

        logger.info(
            "metrics_service_product_deleted",
            extra={
                "restaurant_id": restaurant_id,
                "amount": amount,
            },
        )

        metrics = await self.repo.decrement_products_count(
            restaurant_id=restaurant_id,
            amount=amount,
        )

        if not metrics:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "metrics_product_deleted_updated",
            extra={
                "restaurant_id": restaurant_id,
                "products_count": metrics.products_count,
            },
        )

        return RestaurantMetricResponse.model_validate(metrics)

    # ==============================================
    # CATEGORY CREATED
    # ==============================================

    async def category_created(
        self,
        *,
        restaurant_id: int,
        amount: int = 1,
    ) -> RestaurantMetricResponse:
        """
        تحديث المقاييس عند إنشاء تصنيف جديد.
        
        Args:
            restaurant_id: معرف المطعم
            amount: عدد التصنيفات المضافة
            
        Returns:
            RestaurantMetricResponse: بيانات المقاييس المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المقاييس
        """
        if amount <= 0:
            raise ValidationError(
                message="العدد يجب أن يكون أكبر من الصفر",
            )

        logger.info(
            "metrics_service_category_created",
            extra={
                "restaurant_id": restaurant_id,
                "amount": amount,
            },
        )

        metrics = await self.repo.increment_categories_count(
            restaurant_id=restaurant_id,
            amount=amount,
        )

        if not metrics:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "metrics_category_created_updated",
            extra={
                "restaurant_id": restaurant_id,
                "categories_count": metrics.categories_count,
            },
        )

        return RestaurantMetricResponse.model_validate(metrics)

    # ==============================================
    # CATEGORY DELETED
    # ==============================================

    async def category_deleted(
        self,
        *,
        restaurant_id: int,
        amount: int = 1,
    ) -> RestaurantMetricResponse:
        """
        تحديث المقاييس عند حذف تصنيف.
        
        Args:
            restaurant_id: معرف المطعم
            amount: عدد التصنيفات المحذوفة
            
        Returns:
            RestaurantMetricResponse: بيانات المقاييس المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المقاييس
        """
        if amount <= 0:
            raise ValidationError(
                message="العدد يجب أن يكون أكبر من الصفر",
            )

        logger.info(
            "metrics_service_category_deleted",
            extra={
                "restaurant_id": restaurant_id,
                "amount": amount,
            },
        )

        metrics = await self.repo.decrement_categories_count(
            restaurant_id=restaurant_id,
            amount=amount,
        )

        if not metrics:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "metrics_category_deleted_updated",
            extra={
                "restaurant_id": restaurant_id,
                "categories_count": metrics.categories_count,
            },
        )

        return RestaurantMetricResponse.model_validate(metrics)

    # ==============================================
    # ORDER REGISTERED
    # ==============================================

    async def order_registered(
        self,
        *,
        restaurant_id: int,
        order_total: float,
    ) -> RestaurantMetricResponse:
        """
        تحديث المقاييس عند تسجيل طلب جديد.
        
        Args:
            restaurant_id: معرف المطعم
            order_total: إجمالي قيمة الطلب
            
        Returns:
            RestaurantMetricResponse: بيانات المقاييس المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المقاييس
            ValidationError: إذا كانت قيمة الطلب غير صالحة
        """
        if order_total <= 0:
            raise ValidationError(
                message="قيمة الطلب يجب أن تكون أكبر من الصفر",
            )

        logger.info(
            "metrics_service_order_registered",
            extra={
                "restaurant_id": restaurant_id,
                "order_total": order_total,
            },
        )

        metrics = await self.repo.register_order(
            restaurant_id=restaurant_id,
            order_total=order_total,
        )

        if not metrics:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "metrics_order_registered_updated",
            extra={
                "restaurant_id": restaurant_id,
                "monthly_orders": metrics.monthly_orders,
                "average_order_value": metrics.average_order_value,
            },
        )

        return RestaurantMetricResponse.model_validate(metrics)

    # ==============================================
    # RESET METRICS
    # ==============================================

    async def reset_metrics(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantMetricResponse:
        """
        إعادة تعيين مقاييس المطعم إلى الصفر.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantMetricResponse: بيانات المقاييس المعاد تعيينها
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المقاييس
        """
        logger.info(
            "metrics_service_reset",
            extra={"restaurant_id": restaurant_id},
        )

        metrics = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not metrics:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        data: MetricsDict = {
            "products_count": 0,
            "categories_count": 0,
            "monthly_orders": 0,
            "average_order_value": 0,
        }

        updated = await self.repo.update(
            id=metrics.restaurant_id,
            data=data,
        )

        if not updated:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "metrics_reset_successfully",
            extra={"restaurant_id": restaurant_id},
        )

        return RestaurantMetricResponse.model_validate(updated)

    # ==============================================
    # UPDATE METRICS
    # ==============================================

    async def update_metrics(
        self,
        *,
        restaurant_id: int,
        update_data: RestaurantMetricUpdate,
    ) -> RestaurantMetricResponse:
        """
        تحديث مقاييس المطعم.
        
        Args:
            restaurant_id: معرف المطعم
            update_data: بيانات التحديث
            
        Returns:
            RestaurantMetricResponse: بيانات المقاييس المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المقاييس
            ValidationError: إذا كانت البيانات غير صالحة
        """
        logger.info(
            "metrics_service_update",
            extra={
                "restaurant_id": restaurant_id,
                "fields": list(update_data.model_dump(exclude_unset=True).keys()),
            },
        )

        metrics = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not metrics:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        updates = update_data.model_dump(exclude_unset=True)

        # التحقق من صحة القيم
        if "products_count" in updates and updates["products_count"] < 0:
            raise ValidationError(
                message="عدد المنتجات لا يمكن أن يكون سالباً",
            )

        if "categories_count" in updates and updates["categories_count"] < 0:
            raise ValidationError(
                message="عدد التصنيفات لا يمكن أن يكون سالباً",
            )

        if "monthly_orders" in updates and updates["monthly_orders"] < 0:
            raise ValidationError(
                message="عدد الطلبات الشهرية لا يمكن أن يكون سالباً",
            )

        if "average_order_value" in updates and updates["average_order_value"] < 0:
            raise ValidationError(
                message="متوسط قيمة الطلب لا يمكن أن يكون سالباً",
            )

        updated = await self.repo.update(
            id=metrics.restaurant_id,
            data=updates,
        )

        if not updated:
            raise NotFoundError(
                message=f"مقاييس المطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "metrics_updated_successfully",
            extra={
                "restaurant_id": restaurant_id,
                "updated_fields": list(updates.keys()),
            },
        )

        return RestaurantMetricResponse.model_validate(updated)


# ==============================================
# 🔄 COMPATIBILITY FUNCTIONS
# دوال متوافقة مع الاستيرادات القديمة
# ==============================================

# ==============================================
# INITIALIZE METRICS (COMPATIBILITY)
# ==============================================

async def initialize_metrics(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    تهيئة مقاييس مطعم جديد (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        ValidationError: إذا كانت المقاييس موجودة مسبقاً
    """
    service = RestaurantMetricsService(session=session)

    await service.initialize_metrics(restaurant_id=restaurant_id)

    logger.info(
        "metrics_initialized",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# PRODUCT CREATED (COMPATIBILITY)
# ==============================================

async def product_created(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    تحديث المقاييس عند إنشاء منتج جديد (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المقاييس
    """
    service = RestaurantMetricsService(session=session)

    await service.product_created(restaurant_id=restaurant_id)

    logger.info(
        "metrics_product_created",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# PRODUCT DELETED (COMPATIBILITY)
# ==============================================

async def product_deleted(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    تحديث المقاييس عند حذف منتج (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المقاييس
    """
    service = RestaurantMetricsService(session=session)

    await service.product_deleted(restaurant_id=restaurant_id)

    logger.info(
        "metrics_product_deleted",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# CATEGORY CREATED (COMPATIBILITY)
# ==============================================

async def category_created(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    تحديث المقاييس عند إنشاء تصنيف جديد (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المقاييس
    """
    service = RestaurantMetricsService(session=session)

    await service.category_created(restaurant_id=restaurant_id)

    logger.info(
        "metrics_category_created",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# CATEGORY DELETED (COMPATIBILITY)
# ==============================================

async def category_deleted(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    تحديث المقاييس عند حذف تصنيف (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المقاييس
    """
    service = RestaurantMetricsService(session=session)

    await service.category_deleted(restaurant_id=restaurant_id)

    logger.info(
        "metrics_category_deleted",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# ORDER REGISTERED (COMPATIBILITY)
# ==============================================

async def order_registered(
    *,
    restaurant_id: int,
    order_total: float,
    session: AsyncSession,
) -> None:
    """
    تحديث المقاييس عند تسجيل طلب جديد (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        order_total: إجمالي قيمة الطلب
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المقاييس
        ValidationError: إذا كانت قيمة الطلب غير صالحة
    """
    service = RestaurantMetricsService(session=session)

    await service.order_registered(
        restaurant_id=restaurant_id,
        order_total=order_total,
    )

    logger.info(
        "metrics_order_registered",
        extra={
            "restaurant_id": restaurant_id,
            "order_total": order_total,
        },
    )


# ==============================================
# GET METRICS (COMPATIBILITY)
# ==============================================

async def get_metrics(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> Optional[MetricsDict]:
    """
    الحصول على مقاييس مطعم معين (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        Optional[MetricsDict]: قاموس مقاييس المطعم أو None
    """
    service = RestaurantMetricsService(session=session)

    return await service.get_metrics_dict(restaurant_id=restaurant_id)


# ==============================================
# GET METRICS SUMMARY (COMPATIBILITY)
# ==============================================

async def get_metrics_summary(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> Optional[MetricsDict]:
    """
    الحصول على ملخص مقاييس المطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        Optional[MetricsDict]: قاموس ملخص المقاييس أو None
    """
    service = RestaurantMetricsService(session=session)

    try:
        summary = await service.get_metrics_summary(restaurant_id=restaurant_id)
        return summary.model_dump()
    except NotFoundError:
        return None


# ==============================================
# RESET METRICS (COMPATIBILITY)
# ==============================================

async def reset_metrics(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    إعادة تعيين مقاييس المطعم إلى الصفر (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المقاييس
    """
    service = RestaurantMetricsService(session=session)

    await service.reset_metrics(restaurant_id=restaurant_id)

    logger.info(
        "metrics_reset",
        extra={"restaurant_id": restaurant_id},
    )
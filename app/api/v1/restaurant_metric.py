# ==============================================
# 📊 RESTAURANT METRICS API
# نقاط نهاية API لمقاييس المطعم
# تدير عمليات استعراض وتحديث مقاييس المطعم
# ==============================================

from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Path,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

# ✅ استيراد الاستثناءات
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
)

from app.core.database import get_db
from app.core.logger import logger
from app.schemas.restaurant_metric import (
    MetricsTrend,
    ProductMetrics,
    RestaurantMetricResponse,
    RestaurantMetricSummary,
    RestaurantMetricUpdate,
    RestaurantMetricListResponse,
)
from app.repositories.products_repo import ProductRepository
from app.services.business.restaurant_metrics_service import (
    RestaurantMetricsService,
)
from app.services.business.restaurant_service import RestaurantService

# ==============================================
# 🧩 TYPES
# ==============================================

MetricsTrendList = List[MetricsTrend]


# ==============================================
# 🏗️ ROUTER
# ==============================================

router = APIRouter(
    prefix="/restaurant-metrics",
    tags=["Restaurant Metrics"],
)


# ==============================================
# 🔧 DEPENDENCIES
# ==============================================

async def get_metrics_service(
    session: AsyncSession = Depends(get_db),
) -> RestaurantMetricsService:
    """
    الحصول على خدمة مقاييس المطعم.
    
    Args:
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        RestaurantMetricsService: مثيل من RestaurantMetricsService
    """
    return RestaurantMetricsService(session)


async def get_restaurant_service(
    session: AsyncSession = Depends(get_db),
) -> RestaurantService:
    """
    الحصول على خدمة المطاعم.
    
    Args:
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        RestaurantService: مثيل من RestaurantService
    """
    return RestaurantService(session)


# ==============================================
# 📋 ENDPOINTS
# ==============================================

# ==============================================
# GET RESTAURANT METRICS
# ==============================================

@router.get(
    "/{restaurant_id}",
    response_model=RestaurantMetricResponse,
    summary="مقاييس المطعم",
    description="الحصول على مقاييس مطعم معين",
)
async def get_restaurant_metrics(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantMetricsService = Depends(get_metrics_service),
) -> RestaurantMetricResponse:
    """
    الحصول على مقاييس مطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة مقاييس المطعم
        
    Returns:
        RestaurantMetricResponse: مقاييس المطعم
        
    Raises:
        HTTPException: إذا لم يتم العثور على المقاييس
    """
    logger.info(
        "api_get_restaurant_metrics",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        metrics = await service.get_metrics(
            restaurant_id=restaurant_id,
        )
        return metrics

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_metrics_not_found",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_get_restaurant_metrics_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب مقاييس المطعم",
        )


# ==============================================
# UPDATE RESTAURANT METRICS
# ==============================================

@router.patch(
    "/{restaurant_id}",
    response_model=RestaurantMetricResponse,
    summary="تحديث مقاييس المطعم",
    description="تحديث مقاييس مطعم معين",
)
async def update_restaurant_metrics(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    data: RestaurantMetricUpdate,
    service: RestaurantMetricsService = Depends(get_metrics_service),
) -> RestaurantMetricResponse:
    """
    تحديث مقاييس مطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        data: بيانات التحديث
        service: خدمة مقاييس المطعم
        
    Returns:
        RestaurantMetricResponse: مقاييس المطعم المحدثة
        
    Raises:
        HTTPException: إذا لم يتم العثور على المقاييس
    """
    logger.info(
        "api_update_restaurant_metrics",
        extra={
            "restaurant_id": restaurant_id,
            "fields": list(data.model_dump(exclude_unset=True).keys()),
        },
    )

    try:
        metrics = await service.update_metrics(
            restaurant_id=restaurant_id,
            update_data=data,
        )
        return metrics

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_metrics_not_found_for_update",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationError as e:
        logger.warning(
            "api_update_restaurant_metrics_validation_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_update_restaurant_metrics_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تحديث مقاييس المطعم",
        )


# ==============================================
# INITIALIZE RESTAURANT METRICS
# ==============================================

@router.post(
    "/{restaurant_id}/initialize",
    response_model=RestaurantMetricResponse,
    status_code=status.HTTP_201_CREATED,
    summary="تهيئة مقاييس المطعم",
    description="تهيئة مقاييس جديدة لمطعم",
)
async def initialize_restaurant_metrics(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantMetricsService = Depends(get_metrics_service),
    restaurant_service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantMetricResponse:
    """
    تهيئة مقاييس جديدة لمطعم.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة مقاييس المطعم
        restaurant_service: خدمة المطاعم
        
    Returns:
        RestaurantMetricResponse: المقاييس المهيأة
        
    Raises:
        HTTPException: إذا لم يتم العثور على المطعم أو كانت المقاييس موجودة
    """
    logger.info(
        "api_initialize_restaurant_metrics",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        # التحقق من وجود المطعم
        await restaurant_service.get_restaurant(
            restaurant_id=restaurant_id,
        )

        # تهيئة المقاييس
        metrics = await service.initialize_metrics(
            restaurant_id=restaurant_id,
        )
        return metrics

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_not_found_for_metrics",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationError as e:
        logger.warning(
            "api_restaurant_metrics_already_exist",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_initialize_restaurant_metrics_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تهيئة مقاييس المطعم",
        )


# ==============================================
# RESET RESTAURANT METRICS
# ==============================================

@router.post(
    "/{restaurant_id}/reset",
    response_model=RestaurantMetricResponse,
    summary="إعادة تعيين مقاييس المطعم",
    description="إعادة تعيين مقاييس المطعم إلى الصفر",
)
async def reset_restaurant_metrics(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantMetricsService = Depends(get_metrics_service),
) -> RestaurantMetricResponse:
    """
    إعادة تعيين مقاييس المطعم إلى الصفر.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة مقاييس المطعم
        
    Returns:
        RestaurantMetricResponse: المقاييس المعاد تعيينها
        
    Raises:
        HTTPException: إذا لم يتم العثور على المقاييس
    """
    logger.info(
        "api_reset_restaurant_metrics",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        metrics = await service.reset_metrics(
            restaurant_id=restaurant_id,
        )
        return metrics

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_metrics_not_found_for_reset",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_reset_restaurant_metrics_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء إعادة تعيين مقاييس المطعم",
        )


# ==============================================
# GET RESTAURANT METRICS SUMMARY
# ==============================================

@router.get(
    "/{restaurant_id}/summary",
    response_model=RestaurantMetricSummary,
    summary="ملخص مقاييس المطعم",
    description="الحصول على ملخص مقاييس مطعم معين",
)
async def get_restaurant_metrics_summary(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantMetricsService = Depends(get_metrics_service),
) -> RestaurantMetricSummary:
    """
    الحصول على ملخص مقاييس مطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة مقاييس المطعم
        
    Returns:
        RestaurantMetricSummary: ملخص مقاييس المطعم
        
    Raises:
        HTTPException: إذا لم يتم العثور على المقاييس
    """
    logger.info(
        "api_get_restaurant_metrics_summary",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        summary = await service.get_metrics_summary(
            restaurant_id=restaurant_id,
        )
        return summary

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_metrics_not_found_for_summary",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_get_restaurant_metrics_summary_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب ملخص مقاييس المطعم",
        )


# ==============================================
# GET PRODUCT METRICS
# ==============================================

@router.get(
    "/{restaurant_id}/products",
    response_model=ProductMetrics,
    summary="مقاييس المنتجات",
    description="الحصول على مقاييس المنتجات لمطعم معين",
)
async def get_product_metrics(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantMetricsService = Depends(get_metrics_service),
) -> ProductMetrics:
    """
    الحصول على مقاييس المنتجات لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة مقاييس المطعم
        
    Returns:
        ProductMetrics: مقاييس المنتجات
        
    Raises:
        HTTPException: إذا لم يتم العثور على المقاييس
    """
    logger.info(
        "api_get_product_metrics",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        # الحصول على المقاييس
        metrics = await service.get_metrics(
            restaurant_id=restaurant_id,
        )

        # جلب المنتجات الفعلية لحساب الأسعار
        product_repo = ProductRepository(service.session)
        products = await product_repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
            only_available=False,
        )

        total_products = len(products)
        available_products = sum(1 for product in products if product.is_available)
        unavailable_products = total_products - available_products

        prices = [product.price for product in products] if products else [0]

        return ProductMetrics(
            restaurant_id=restaurant_id,
            total_products=total_products,
            available_products=available_products,
            unavailable_products=unavailable_products,
            most_expensive=max(prices) if prices else 0,
            least_expensive=min(prices) if prices else 0,
            avg_price=sum(prices) / len(prices) if prices else 0,
        )

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_metrics_not_found_for_products",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_get_product_metrics_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب مقاييس المنتجات",
        )


# ==============================================
# GET METRICS TREND
# ==============================================

@router.get(
    "/{restaurant_id}/trend",
    response_model=MetricsTrend,
    summary="اتجاه المقاييس",
    description="الحصول على اتجاه مقاييس مطعم معين",
)
async def get_metrics_trend(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    period: str = Query(
        "monthly",
        description="الفترة: daily, weekly, monthly",
        pattern="^(daily|weekly|monthly)$",
    ),
    service: RestaurantMetricsService = Depends(get_metrics_service),
) -> MetricsTrend:
    """
    الحصول على اتجاه مقاييس مطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        period: الفترة (daily, weekly, monthly)
        service: خدمة مقاييس المطعم
        
    Returns:
        MetricsTrend: اتجاه المقاييس
        
    Raises:
        HTTPException: إذا لم يتم العثور على المقاييس
    """
    logger.info(
        "api_get_metrics_trend",
        extra={
            "restaurant_id": restaurant_id,
            "period": period,
        },
    )

    try:
        # الحصول على المقاييس
        metrics = await service.get_metrics(
            restaurant_id=restaurant_id,
        )

        # بناء نقاط الاتجاه (محاكاة - سيتم استبدالها ببيانات حقيقية)
        from datetime import datetime
        import calendar

        trend_points = []
        total_orders = metrics.monthly_orders or 0
        total_revenue = metrics.average_order_value * total_orders

        # إنشاء نقاط افتراضية للشهر الحالي
        now = datetime.now()
        _, days_in_month = calendar.monthrange(now.year, now.month)

        days_to_show = min(days_in_month, 30)

        for day in range(1, days_to_show + 1):
            day_orders = max(1, int(total_orders / 30))
            day_revenue = day_orders * (metrics.average_order_value or 100)

            trend_points.append({
                "period": f"{now.year}-{now.month:02d}-{day:02d}",
                "orders_count": day_orders,
                "revenue": day_revenue,
                "avg_order_value": metrics.average_order_value or 100,
            })

        return MetricsTrend(
            restaurant_id=restaurant_id,
            trend=trend_points,
            total_orders=total_orders,
            total_revenue=total_revenue,
            overall_avg=metrics.average_order_value or 0,
        )

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_metrics_not_found_for_trend",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_get_metrics_trend_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب اتجاه المقاييس",
        )


# ==============================================
# SIMULATE ORDER (FOR TESTING)
# ==============================================

@router.post(
    "/{restaurant_id}/simulate-order",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="محاكاة طلب (للاختبار)",
    description="محاكاة طلب جديد لتحديث المقاييس (للاختبار فقط)",
)
async def simulate_order(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    order_total: float = Query(
        100.00,
        gt=0,
        description="قيمة الطلب",
    ),
    service: RestaurantMetricsService = Depends(get_metrics_service),
) -> None:
    """
    محاكاة طلب جديد لتحديث المقاييس (للاختبار فقط).
    
    Args:
        restaurant_id: معرف المطعم
        order_total: قيمة الطلب
        service: خدمة مقاييس المطعم
        
    Raises:
        HTTPException: إذا لم يتم العثور على المقاييس
    """
    logger.info(
        "api_simulate_order",
        extra={
            "restaurant_id": restaurant_id,
            "order_total": order_total,
        },
    )

    try:
        await service.order_registered(
            restaurant_id=restaurant_id,
            order_total=order_total,
        )

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_metrics_not_found_for_simulate",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationError as e:
        logger.warning(
            "api_simulate_order_validation_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_simulate_order_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء محاكاة الطلب",
        )

    logger.info(
        "api_simulate_order_successful",
        extra={
            "restaurant_id": restaurant_id,
            "order_total": order_total,
        },
    )
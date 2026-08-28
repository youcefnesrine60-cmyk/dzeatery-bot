# ==============================================
# 🔢 RESTAURANT ORDER COUNTER API
# نقاط نهاية API لعداد طلبات المطعم
# تدير عمليات إنشاء واستعراض وتحديث عداد طلبات المطعم
# ==============================================

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
    ConflictError,
    NotFoundError,
    ValidationError,
)

from app.core.database import get_db
from app.core.logger import logger
from app.schemas.restaurant_order_counter import (
    NextOrderNumberResponse,
    OrderCounterSummary,
    OrderNumberFormat,
    RestaurantOrderCounterResponse,
    RestaurantOrderCounterUpdate,
    RestaurantOrderCounterListResponse,
)
from app.services.business.restaurant_order_counter_service import (
    RestaurantOrderCounterService,
)
from app.services.business.restaurant_service import RestaurantService

# ==============================================
# 🏗️ ROUTER
# ==============================================

router = APIRouter(
    prefix="/restaurant-order-counters",
    tags=["Restaurant Order Counters"],
)


# ==============================================
# 🔧 DEPENDENCIES
# ==============================================

async def get_order_counter_service(
    session: AsyncSession = Depends(get_db),
) -> RestaurantOrderCounterService:
    """
    الحصول على خدمة عداد طلبات المطعم.
    
    Args:
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        RestaurantOrderCounterService: مثيل من RestaurantOrderCounterService
    """
    return RestaurantOrderCounterService(session)


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
# LIST ORDER COUNTERS
# ==============================================

@router.get(
    "/",
    response_model=RestaurantOrderCounterListResponse,
    summary="قائمة عدادات الطلبات",
    description="الحصول على قائمة عدادات طلبات المطاعم",
)
async def list_order_counters(
    *,
    skip: int = Query(
        0,
        ge=0,
        description="عدد السجلات للتخطي",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=200,
        description="الحد الأقصى للسجلات",
    ),
    service: RestaurantOrderCounterService = Depends(get_order_counter_service),
) -> RestaurantOrderCounterListResponse:
    """
    الحصول على قائمة عدادات طلبات المطاعم.
    
    Args:
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        service: خدمة عداد طلبات المطعم
        
    Returns:
        RestaurantOrderCounterListResponse: قائمة عدادات الطلبات مع الإحصائيات
    """
    logger.info(
        "api_list_order_counters",
        extra={
            "skip": skip,
            "limit": limit,
        },
    )

    try:
        counters = await service.repo.get_all(
            skip=skip,
            limit=limit,
            order_by="restaurant_id",
        )
        total = await service.repo.count()

        return RestaurantOrderCounterListResponse(
            items=[RestaurantOrderCounterResponse.model_validate(c) for c in counters],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.exception(
            "api_list_order_counters_error",
            extra={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب قائمة عدادات الطلبات",
        )


# ==============================================
# GET ORDER COUNTER
# ==============================================

@router.get(
    "/{restaurant_id}",
    response_model=RestaurantOrderCounterResponse,
    summary="عداد طلبات المطعم",
    description="الحصول على عداد طلبات مطعم معين",
)
async def get_order_counter(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantOrderCounterService = Depends(get_order_counter_service),
) -> RestaurantOrderCounterResponse:
    """
    الحصول على عداد طلبات مطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة عداد طلبات المطعم
        
    Returns:
        RestaurantOrderCounterResponse: عداد طلبات المطعم
        
    Raises:
        HTTPException: إذا لم يتم العثور على العداد
    """
    logger.info(
        "api_get_order_counter",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        counter = await service.get_counter(
            restaurant_id=restaurant_id,
        )
        return counter

    except NotFoundError as e:
        logger.warning(
            "api_order_counter_not_found",
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
            "api_get_order_counter_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب عداد الطلبات",
        )


# ==============================================
# INITIALIZE ORDER COUNTER
# ==============================================

@router.post(
    "/{restaurant_id}/initialize",
    response_model=RestaurantOrderCounterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="تهيئة عداد طلبات المطعم",
    description="تهيئة عداد طلبات جديد لمطعم",
)
async def initialize_order_counter(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantOrderCounterService = Depends(get_order_counter_service),
    restaurant_service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantOrderCounterResponse:
    """
    تهيئة عداد طلبات جديد لمطعم.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة عداد طلبات المطعم
        restaurant_service: خدمة المطاعم
        
    Returns:
        RestaurantOrderCounterResponse: العداد المهيأ
        
    Raises:
        HTTPException: إذا لم يتم العثور على المطعم أو كان العداد موجوداً
    """
    logger.info(
        "api_initialize_order_counter",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        # التحقق من وجود المطعم
        await restaurant_service.get_restaurant(
            restaurant_id=restaurant_id,
        )

        # تهيئة العداد
        counter = await service.initialize_counter(
            restaurant_id=restaurant_id,
        )
        return counter

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_not_found_for_counter",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ConflictError as e:
        logger.warning(
            "api_order_counter_already_exists",
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
            "api_initialize_order_counter_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تهيئة عداد الطلبات",
        )


# ==============================================
# UPDATE ORDER COUNTER
# ==============================================

@router.patch(
    "/{restaurant_id}",
    response_model=RestaurantOrderCounterResponse,
    summary="تحديث عداد طلبات المطعم",
    description="تحديث عداد طلبات مطعم معين",
)
async def update_order_counter(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    data: RestaurantOrderCounterUpdate,
    service: RestaurantOrderCounterService = Depends(get_order_counter_service),
) -> RestaurantOrderCounterResponse:
    """
    تحديث عداد طلبات مطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        data: بيانات التحديث
        service: خدمة عداد طلبات المطعم
        
    Returns:
        RestaurantOrderCounterResponse: العداد المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على العداد
    """
    logger.info(
        "api_update_order_counter",
        extra={
            "restaurant_id": restaurant_id,
            "fields": list(data.model_dump(exclude_unset=True).keys()),
        },
    )

    try:
        counter = await service.update_counter(
            restaurant_id=restaurant_id,
            update_data=data,
        )
        return counter

    except NotFoundError as e:
        logger.warning(
            "api_order_counter_not_found_for_update",
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
            "api_update_order_counter_validation_error",
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
            "api_update_order_counter_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تحديث عداد الطلبات",
        )


# ==============================================
# GENERATE NEXT ORDER NUMBER
# ==============================================

@router.post(
    "/{restaurant_id}/next",
    response_model=NextOrderNumberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="توليد رقم الطلب التالي",
    description="توليد رقم الطلب التالي لمطعم معين",
)
async def generate_next_order_number(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantOrderCounterService = Depends(get_order_counter_service),
) -> NextOrderNumberResponse:
    """
    توليد رقم الطلب التالي لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة عداد طلبات المطعم
        
    Returns:
        NextOrderNumberResponse: رقم الطلب التالي
        
    Raises:
        HTTPException: إذا لم يتم العثور على العداد
    """
    logger.info(
        "api_generate_next_order_number",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        result = await service.generate_next_order_number(
            restaurant_id=restaurant_id,
        )
        return result

    except NotFoundError as e:
        logger.warning(
            "api_order_counter_not_found_for_generate",
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
            "api_generate_next_order_number_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء توليد رقم الطلب التالي",
        )


# ==============================================
# GET ORDER COUNTER SUMMARY
# ==============================================

@router.get(
    "/{restaurant_id}/summary",
    response_model=OrderCounterSummary,
    summary="ملخص عداد طلبات المطعم",
    description="الحصول على ملخص عداد طلبات مطعم معين",
)
async def get_order_counter_summary(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantOrderCounterService = Depends(get_order_counter_service),
) -> OrderCounterSummary:
    """
    الحصول على ملخص عداد طلبات مطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة عداد طلبات المطعم
        
    Returns:
        OrderCounterSummary: ملخص عداد طلبات المطعم
        
    Raises:
        HTTPException: إذا لم يتم العثور على العداد
    """
    logger.info(
        "api_get_order_counter_summary",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        summary = await service.get_counter_summary(
            restaurant_id=restaurant_id,
        )
        return summary

    except Exception as e:
        logger.exception(
            "api_get_order_counter_summary_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب ملخص عداد الطلبات",
        )


# ==============================================
# GET ORDER NUMBER FORMAT
# ==============================================

@router.get(
    "/{restaurant_id}/format",
    response_model=OrderNumberFormat,
    summary="تنسيق رقم الطلب",
    description="الحصول على تنسيق رقم الطلب لمطعم معين",
)
async def get_order_number_format(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantOrderCounterService = Depends(get_order_counter_service),
) -> OrderNumberFormat:
    """
    الحصول على تنسيق رقم الطلب لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة عداد طلبات المطعم
        
    Returns:
        OrderNumberFormat: تنسيق رقم الطلب
        
    Raises:
        HTTPException: إذا لم يتم العثور على العداد
    """
    logger.info(
        "api_get_order_number_format",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        # الحصول على العداد
        counter = await service.get_counter(
            restaurant_id=restaurant_id,
        )

        # بناء تنسيق رقم الطلب
        sequence = counter.last_number + 1
        example = service.build_order_number(
            restaurant_id=restaurant_id,
            sequence=sequence,
        )

        return OrderNumberFormat(
            restaurant_id=restaurant_id,
            prefix=f"RST{restaurant_id}-",
            sequence=sequence,
            format="RST{restaurant_id}-{sequence:06d}",
            example=example,
        )

    except NotFoundError as e:
        logger.warning(
            "api_order_counter_not_found_for_format",
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
            "api_get_order_number_format_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب تنسيق رقم الطلب",
        )


# ==============================================
# RESET ORDER COUNTER
# ==============================================

@router.post(
    "/{restaurant_id}/reset",
    response_model=RestaurantOrderCounterResponse,
    summary="إعادة تعيين عداد طلبات المطعم",
    description="إعادة تعيين عداد طلبات المطعم إلى الصفر",
)
async def reset_order_counter(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantOrderCounterService = Depends(get_order_counter_service),
) -> RestaurantOrderCounterResponse:
    """
    إعادة تعيين عداد طلبات المطعم إلى الصفر.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة عداد طلبات المطعم
        
    Returns:
        RestaurantOrderCounterResponse: العداد المعاد تعيينه
        
    Raises:
        HTTPException: إذا لم يتم العثور على العداد
    """
    logger.info(
        "api_reset_order_counter",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        counter = await service.reset_counter(
            restaurant_id=restaurant_id,
        )
        return counter

    except NotFoundError as e:
        logger.warning(
            "api_order_counter_not_found_for_reset",
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
            "api_reset_order_counter_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء إعادة تعيين عداد الطلبات",
        )


# ==============================================
# INCREMENT ORDER COUNTER
# ==============================================

@router.post(
    "/{restaurant_id}/increment",
    response_model=RestaurantOrderCounterResponse,
    summary="زيادة عداد طلبات المطعم",
    description="زيادة عداد طلبات المطعم بمقدار 1",
)
async def increment_order_counter(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantOrderCounterService = Depends(get_order_counter_service),
) -> RestaurantOrderCounterResponse:
    """
    زيادة عداد طلبات المطعم بمقدار 1.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة عداد طلبات المطعم
        
    Returns:
        RestaurantOrderCounterResponse: العداد المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على العداد
    """
    logger.info(
        "api_increment_order_counter",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        counter = await service.increment_counter(
            restaurant_id=restaurant_id,
        )
        return counter

    except NotFoundError as e:
        logger.warning(
            "api_order_counter_not_found_for_increment",
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
            "api_increment_order_counter_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء زيادة عداد الطلبات",
        )
# ==============================================
# 🏦 RESTAURANT PAYMENT SETTINGS API
# نقاط نهاية API لإعدادات الدفع للمطعم
# تدير عمليات إنشاء واستعراض وتحديث وحذف إعدادات الدفع
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
from app.schemas.restaurant_payment_setting import (
    PaymentMethodsList,
    PaymentSettingsSummary,
    RestaurantPaymentSettingCreate,
    RestaurantPaymentSettingResponse,
    RestaurantPaymentSettingUpdate,
    RestaurantPaymentSettingListResponse,
)
from app.services.business.restaurant_payment_settings_service import (
    RestaurantPaymentSettingsService,
)

# ==============================================
# 🧩 CONSTANTS
# ==============================================

ALL_PAYMENT_METHODS = ["cash", "card", "ccp", "baridimob", "stripe", "paypal"]


# ==============================================
# 🏗️ ROUTER
# ==============================================

router = APIRouter(
    prefix="/restaurant-payment-settings",
    tags=["Restaurant Payment Settings"],
)


# ==============================================
# 🔧 DEPENDENCIES
# ==============================================

async def get_payment_settings_service(
    session: AsyncSession = Depends(get_db),
) -> RestaurantPaymentSettingsService:
    """
    الحصول على خدمة إعدادات الدفع.
    
    Args:
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        RestaurantPaymentSettingsService: مثيل من RestaurantPaymentSettingsService
    """
    return RestaurantPaymentSettingsService(session)


# ==============================================
# 📋 ENDPOINTS
# ==============================================

# ==============================================
# LIST PAYMENT SETTINGS
# ==============================================

@router.get(
    "/",
    response_model=RestaurantPaymentSettingListResponse,
    summary="قائمة إعدادات الدفع",
    description="الحصول على قائمة إعدادات الدفع للمطاعم",
)
async def list_payment_settings(
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
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> RestaurantPaymentSettingListResponse:
    """
    الحصول على قائمة إعدادات الدفع للمطاعم.
    
    Args:
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        service: خدمة إعدادات الدفع
        
    Returns:
        RestaurantPaymentSettingListResponse: قائمة إعدادات الدفع مع الإحصائيات
    """
    logger.info(
        "api_list_payment_settings",
        extra={
            "skip": skip,
            "limit": limit,
        },
    )

    try:
        settings = await service.repo.get_all(
            skip=skip,
            limit=limit,
            order_by="restaurant_id",
        )
        total = await service.repo.count()

        return RestaurantPaymentSettingListResponse(
            items=[RestaurantPaymentSettingResponse.model_validate(s) for s in settings],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.exception(
            "api_list_payment_settings_error",
            extra={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب قائمة إعدادات الدفع",
        )


# ==============================================
# GET PAYMENT SETTINGS
# ==============================================

@router.get(
    "/{restaurant_id}",
    response_model=RestaurantPaymentSettingResponse,
    summary="إعدادات الدفع للمطعم",
    description="الحصول على إعدادات الدفع لمطعم معين",
)
async def get_payment_settings(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> RestaurantPaymentSettingResponse:
    """
    الحصول على إعدادات الدفع لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة إعدادات الدفع
        
    Returns:
        RestaurantPaymentSettingResponse: إعدادات الدفع
        
    Raises:
        HTTPException: إذا لم يتم العثور على الإعدادات
    """
    logger.info(
        "api_get_payment_settings",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        settings = await service.get_settings(
            restaurant_id=restaurant_id,
        )
        return settings

    except NotFoundError as e:
        logger.warning(
            "api_payment_settings_not_found",
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
            "api_get_payment_settings_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب إعدادات الدفع",
        )


# ==============================================
# CREATE PAYMENT SETTINGS
# ==============================================

@router.post(
    "/",
    response_model=RestaurantPaymentSettingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="إنشاء إعدادات دفع",
    description="إنشاء إعدادات دفع جديدة لمطعم",
)
async def create_payment_settings(
    *,
    data: RestaurantPaymentSettingCreate,
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> RestaurantPaymentSettingResponse:
    """
    إنشاء إعدادات دفع جديدة لمطعم.
    
    Args:
        data: بيانات إعدادات الدفع
        service: خدمة إعدادات الدفع
        
    Returns:
        RestaurantPaymentSettingResponse: إعدادات الدفع المنشأة
        
    Raises:
        HTTPException: إذا كانت الإعدادات موجودة مسبقاً أو حدث خطأ
    """
    logger.info(
        "api_create_payment_settings",
        extra={
            "restaurant_id": data.restaurant_id,
        },
    )

    try:
        settings = await service.create_settings(
            settings_data=data,
        )
        return settings

    except ConflictError as e:
        logger.warning(
            "api_payment_settings_already_exist",
            extra={
                "restaurant_id": data.restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValidationError as e:
        logger.warning(
            "api_create_payment_settings_validation_error",
            extra={
                "restaurant_id": data.restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_create_payment_settings_error",
            extra={
                "restaurant_id": data.restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء إنشاء إعدادات الدفع",
        )


# ==============================================
# UPDATE PAYMENT SETTINGS
# ==============================================

@router.put(
    "/{restaurant_id}",
    response_model=RestaurantPaymentSettingResponse,
    summary="تحديث إعدادات الدفع",
    description="تحديث إعدادات الدفع لمطعم معين",
)
async def update_payment_settings(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    data: RestaurantPaymentSettingUpdate,
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> RestaurantPaymentSettingResponse:
    """
    تحديث إعدادات الدفع لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        data: بيانات التحديث
        service: خدمة إعدادات الدفع
        
    Returns:
        RestaurantPaymentSettingResponse: إعدادات الدفع المحدثة
        
    Raises:
        HTTPException: إذا لم يتم العثور على الإعدادات
    """
    logger.info(
        "api_update_payment_settings",
        extra={
            "restaurant_id": restaurant_id,
            "fields": list(data.model_dump(exclude_unset=True).keys()),
        },
    )

    try:
        settings = await service.update_settings(
            restaurant_id=restaurant_id,
            update_data=data,
        )
        return settings

    except NotFoundError as e:
        logger.warning(
            "api_payment_settings_not_found_for_update",
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
            "api_update_payment_settings_validation_error",
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
            "api_update_payment_settings_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تحديث إعدادات الدفع",
        )


# ==============================================
# DELETE PAYMENT SETTINGS
# ==============================================

@router.delete(
    "/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف إعدادات الدفع",
    description="حذف إعدادات الدفع لمطعم معين",
)
async def delete_payment_settings(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> None:
    """
    حذف إعدادات الدفع لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة إعدادات الدفع
        
    Raises:
        HTTPException: إذا لم يتم العثور على الإعدادات
    """
    logger.info(
        "api_delete_payment_settings",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        await service.delete_settings(
            restaurant_id=restaurant_id,
        )

    except NotFoundError as e:
        logger.warning(
            "api_payment_settings_not_found_for_delete",
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
            "api_delete_payment_settings_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء حذف إعدادات الدفع",
        )

    logger.info(
        "api_payment_settings_deleted_successfully",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# GET ALLOWED PAYMENT METHODS
# ==============================================

@router.get(
    "/{restaurant_id}/methods",
    response_model=PaymentMethodsList,
    summary="طرق الدفع المسموح بها",
    description="الحصول على قائمة طرق الدفع المسموح بها لمطعم معين",
)
async def get_allowed_payment_methods(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> PaymentMethodsList:
    """
    الحصول على قائمة طرق الدفع المسموح بها لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة إعدادات الدفع
        
    Returns:
        PaymentMethodsList: قائمة طرق الدفع المسموح بها
        
    Raises:
        HTTPException: إذا لم يتم العثور على الإعدادات
    """
    logger.info(
        "api_get_allowed_payment_methods",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        # أولاً التحقق من وجود الإعدادات
        await service.get_settings(restaurant_id=restaurant_id)

        allowed_methods = await service.get_allowed_methods(
            restaurant_id=restaurant_id,
        )

        return PaymentMethodsList(
            restaurant_id=restaurant_id,
            allowed_methods=allowed_methods,
            all_methods=ALL_PAYMENT_METHODS,
        )

    except NotFoundError as e:
        logger.warning(
            "api_payment_settings_not_found_for_methods",
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
            "api_get_allowed_payment_methods_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب طرق الدفع المسموح بها",
        )


# ==============================================
# UPDATE PAYMENT METHODS
# ==============================================

@router.patch(
    "/{restaurant_id}/methods",
    response_model=RestaurantPaymentSettingResponse,
    summary="تحديث طرق الدفع",
    description="تحديث طرق الدفع المسموح بها لمطعم معين",
)
async def update_payment_methods(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    allow_cash: bool = Query(
        True,
        description="السماح بالدفع نقداً",
    ),
    allow_card: bool = Query(
        True,
        description="السماح بالدفع ببطاقة POS",
    ),
    allow_ccp: bool = Query(
        False,
        description="السماح بالدفع عبر CCP",
    ),
    allow_baridimob: bool = Query(
        False,
        description="السماح بالدفع عبر بريدي موب",
    ),
    allow_stripe: bool = Query(
        False,
        description="السماح بالدفع عبر Stripe",
    ),
    allow_paypal: bool = Query(
        False,
        description="السماح بالدفع عبر PayPal",
    ),
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> RestaurantPaymentSettingResponse:
    """
    تحديث طرق الدفع المسموح بها لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        allow_cash: السماح بالدفع نقداً
        allow_card: السماح بالدفع ببطاقة POS
        allow_ccp: السماح بالدفع عبر CCP
        allow_baridimob: السماح بالدفع عبر بريدي موب
        allow_stripe: السماح بالدفع عبر Stripe
        allow_paypal: السماح بالدفع عبر PayPal
        service: خدمة إعدادات الدفع
        
    Returns:
        RestaurantPaymentSettingResponse: إعدادات الدفع المحدثة
        
    Raises:
        HTTPException: إذا لم يتم العثور على الإعدادات
    """
    logger.info(
        "api_update_payment_methods",
        extra={
            "restaurant_id": restaurant_id,
            "allow_cash": allow_cash,
            "allow_card": allow_card,
            "allow_ccp": allow_ccp,
            "allow_baridimob": allow_baridimob,
            "allow_stripe": allow_stripe,
            "allow_paypal": allow_paypal,
        },
    )

    try:
        settings = await service.update_payment_methods(
            restaurant_id=restaurant_id,
            allow_cash=allow_cash,
            allow_card=allow_card,
            allow_ccp=allow_ccp,
            allow_baridimob=allow_baridimob,
            allow_stripe=allow_stripe,
            allow_paypal=allow_paypal,
        )
        return settings

    except NotFoundError as e:
        logger.warning(
            "api_payment_settings_not_found_for_methods_update",
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
            "api_update_payment_methods_validation_error",
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
            "api_update_payment_methods_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تحديث طرق الدفع",
        )


# ==============================================
# GET PAYMENT SETTINGS SUMMARY
# ==============================================

@router.get(
    "/{restaurant_id}/summary",
    response_model=PaymentSettingsSummary,
    summary="ملخص إعدادات الدفع",
    description="الحصول على ملخص إعدادات الدفع لمطعم معين",
)
async def get_payment_settings_summary(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> PaymentSettingsSummary:
    """
    الحصول على ملخص إعدادات الدفع لمطعم معين.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة إعدادات الدفع
        
    Returns:
        PaymentSettingsSummary: ملخص إعدادات الدفع
        
    Raises:
        HTTPException: إذا لم يتم العثور على الإعدادات
    """
    logger.info(
        "api_get_payment_settings_summary",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        summary = await service.get_settings_summary(
            restaurant_id=restaurant_id,
        )
        return summary

    except NotFoundError as e:
        logger.warning(
            "api_payment_settings_not_found_for_summary",
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
            "api_get_payment_settings_summary_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب ملخص إعدادات الدفع",
        )


# ==============================================
# RESET PAYMENT SETTINGS TO DEFAULTS
# ==============================================

@router.post(
    "/{restaurant_id}/reset",
    response_model=RestaurantPaymentSettingResponse,
    summary="إعادة تعيين إعدادات الدفع",
    description="إعادة تعيين إعدادات الدفع إلى القيم الافتراضية",
)
async def reset_payment_settings(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> RestaurantPaymentSettingResponse:
    """
    إعادة تعيين إعدادات الدفع إلى القيم الافتراضية (cash, card فقط).
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة إعدادات الدفع
        
    Returns:
        RestaurantPaymentSettingResponse: إعدادات الدفع المعاد تعيينها
        
    Raises:
        HTTPException: إذا لم يتم العثور على الإعدادات
    """
    logger.info(
        "api_reset_payment_settings",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        settings = await service.reset_to_defaults(
            restaurant_id=restaurant_id,
        )
        return settings

    except NotFoundError as e:
        logger.warning(
            "api_payment_settings_not_found_for_reset",
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
            "api_reset_payment_settings_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء إعادة تعيين إعدادات الدفع",
        )


# ==============================================
# ENABLE PAYMENT METHOD
# ==============================================

@router.post(
    "/{restaurant_id}/methods/{method}/enable",
    response_model=RestaurantPaymentSettingResponse,
    summary="تفعيل طريقة دفع",
    description="تفعيل طريقة دفع معينة لمطعم",
)
async def enable_payment_method(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    method: str = Path(..., description="طريقة الدفع (cash, card, ccp, baridimob, stripe, paypal)"),
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> RestaurantPaymentSettingResponse:
    """
    تفعيل طريقة دفع معينة لمطعم.
    
    Args:
        restaurant_id: معرف المطعم
        method: طريقة الدفع
        service: خدمة إعدادات الدفع
        
    Returns:
        RestaurantPaymentSettingResponse: إعدادات الدفع المحدثة
        
    Raises:
        HTTPException: إذا لم يتم العثور على الإعدادات أو كانت الطريقة غير صالحة
    """
    logger.info(
        "api_enable_payment_method",
        extra={
            "restaurant_id": restaurant_id,
            "method": method,
        },
    )

    try:
        settings = await service.enable_payment_method(
            restaurant_id=restaurant_id,
            method=method,
        )
        return settings

    except NotFoundError as e:
        logger.warning(
            "api_payment_settings_not_found_for_enable",
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
            "api_enable_payment_method_validation_error",
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
            "api_enable_payment_method_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تفعيل طريقة الدفع",
        )


# ==============================================
# DISABLE PAYMENT METHOD
# ==============================================

@router.post(
    "/{restaurant_id}/methods/{method}/disable",
    response_model=RestaurantPaymentSettingResponse,
    summary="إلغاء تفعيل طريقة دفع",
    description="إلغاء تفعيل طريقة دفع معينة لمطعم",
)
async def disable_payment_method(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    method: str = Path(..., description="طريقة الدفع (cash, card, ccp, baridimob, stripe, paypal)"),
    service: RestaurantPaymentSettingsService = Depends(
        get_payment_settings_service,
    ),
) -> RestaurantPaymentSettingResponse:
    """
    إلغاء تفعيل طريقة دفع معينة لمطعم.
    
    Args:
        restaurant_id: معرف المطعم
        method: طريقة الدفع
        service: خدمة إعدادات الدفع
        
    Returns:
        RestaurantPaymentSettingResponse: إعدادات الدفع المحدثة
        
    Raises:
        HTTPException: إذا لم يتم العثور على الإعدادات أو كانت الطريقة غير صالحة
    """
    logger.info(
        "api_disable_payment_method",
        extra={
            "restaurant_id": restaurant_id,
            "method": method,
        },
    )

    try:
        settings = await service.disable_payment_method(
            restaurant_id=restaurant_id,
            method=method,
        )
        return settings

    except NotFoundError as e:
        logger.warning(
            "api_payment_settings_not_found_for_disable",
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
            "api_disable_payment_method_validation_error",
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
            "api_disable_payment_method_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء إلغاء تفعيل طريقة الدفع",
        )
# ==============================================
# 🍽️ RESTAURANT API
# نقاط نهاية API للمطاعم
# تدير عمليات إنشاء واستعراض وتحديث وحذف المطاعم
# ==============================================

from typing import Optional

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
    UnauthorizedError,
)

from app.core.database import get_db
from app.core.logger import logger
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse,
    RestaurantStats,
    RestaurantUpdate,
    RestaurantListResponse,
)
from app.services.business.restaurant_service import RestaurantService

# ==============================================
# 🏗️ ROUTER
# ==============================================

router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"],
)


# ==============================================
# 🔧 DEPENDENCIES
# ==============================================

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
# LIST RESTAURANTS
# ==============================================

@router.get(
    "/",
    response_model=RestaurantListResponse,
    summary="قائمة المطاعم",
    description="الحصول على قائمة المطاعم مع إمكانية التصفية والبحث",
)
async def list_restaurants(
    *,
    owner_id: Optional[int] = Query(
        None,
        description="معرف المالك",
        ge=1,
    ),
    wilaya: Optional[str] = Query(
        None,
        max_length=100,
        description="الولاية",
    ),
    search: Optional[str] = Query(
        None,
        min_length=1,
        max_length=255,
        description="نص البحث",
    ),
    only_active: bool = Query(
        True,
        description="جلب المطاعم النشطة فقط",
    ),
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
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantListResponse:
    """
    الحصول على قائمة المطاعم.
    
    Args:
        owner_id: معرف المالك للتصفية
        wilaya: الولاية للتصفية
        search: نص البحث
        only_active: جلب المطاعم النشطة فقط
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        service: خدمة المطاعم
        
    Returns:
        RestaurantListResponse: قائمة المطاعم مع الإحصائيات
    """
    logger.info(
        "api_list_restaurants",
        extra={
            "owner_id": owner_id,
            "wilaya": wilaya,
            "search": search,
            "only_active": only_active,
            "skip": skip,
            "limit": limit,
        },
    )

    try:
        # تحديد طريقة الجلب بناءً على معايير التصفية
        if owner_id is not None:
            restaurants = await service.get_owner_restaurants(
                owner_id=owner_id,
                skip=skip,
                limit=limit,
                include_inactive=not only_active,
            )
            total = await service.count_owner_restaurants(owner_id=owner_id)
            
        elif wilaya is not None:
            restaurants = await service.get_restaurants_by_wilaya(
                wilaya=wilaya,
                skip=skip,
                limit=limit,
            )
            total = await service.count_restaurants_by_wilaya(wilaya=wilaya)
            
        elif search is not None:
            restaurants = await service.search_restaurants(
                query=search,
                skip=skip,
                limit=limit,
            )
            total = len(restaurants)
            
        else:
            restaurants = await service.get_all_restaurants(
                skip=skip,
                limit=limit,
                only_active=only_active,
            )
            total = len(restaurants)

        return RestaurantListResponse(
            items=restaurants,
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.exception(
            "api_list_restaurants_error",
            extra={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب قائمة المطاعم",
        )


# ==============================================
# GET RESTAURANT BY ID
# ==============================================

@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
    summary="مطعم بالمعرف",
    description="الحصول على مطعم محدد مع جميع علاقاته",
)
async def get_restaurant(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantResponse:
    """
    الحصول على مطعم بالمعرف.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة المطاعم
        
    Returns:
        RestaurantResponse: المطعم المطلوب
        
    Raises:
        HTTPException: إذا لم يتم العثور على المطعم
    """
    logger.info(
        "api_get_restaurant",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        restaurant = await service.get_restaurant_with_details(
            restaurant_id=restaurant_id,
        )
        return restaurant

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_not_found",
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
            "api_get_restaurant_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب المطعم",
        )


# ==============================================
# CREATE RESTAURANT
# ==============================================

@router.post(
    "/",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="إنشاء مطعم",
    description="إنشاء مطعم جديد",
)
async def create_restaurant(
    *,
    data: RestaurantCreate,
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantResponse:
    """
    إنشاء مطعم جديد.
    
    Args:
        data: بيانات المطعم
        service: خدمة المطاعم
        
    Returns:
        RestaurantResponse: المطعم المنشأ
        
    Raises:
        HTTPException: إذا حدث خطأ أثناء الإنشاء
    """
    logger.info(
        "api_create_restaurant",
        extra={
            "owner_id": data.owner_id,
            "restaurant_name": data.name,
            "type": data.type,
            "wilaya": data.wilaya,
        },
    )

    try:
        restaurant = await service.create_restaurant(
            restaurant_data=data,
        )
        return restaurant

    except ConflictError as e:
        logger.warning(
            "api_create_restaurant_conflict",
            extra={
                "owner_id": data.owner_id,
                "name": data.name,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValidationError as e:
        logger.warning(
            "api_create_restaurant_validation_error",
            extra={
                "owner_id": data.owner_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except UnauthorizedError as e:
        logger.warning(
            "api_create_restaurant_unauthorized",
            extra={
                "owner_id": data.owner_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            "api_create_restaurant_error",
            extra={
                "owner_id": data.owner_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء إنشاء المطعم",
        )


# ==============================================
# UPDATE RESTAURANT
# ==============================================

@router.patch(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
    summary="تحديث مطعم",
    description="تحديث بيانات مطعم موجود",
)
async def update_restaurant(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    data: RestaurantUpdate,
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantResponse:
    """
    تحديث مطعم موجود.
    
    Args:
        restaurant_id: معرف المطعم
        data: بيانات التحديث
        service: خدمة المطاعم
        
    Returns:
        RestaurantResponse: المطعم المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على المطعم أو حدث تعارض
    """
    logger.info(
        "api_update_restaurant",
        extra={
            "restaurant_id": restaurant_id,
            "fields": list(data.model_dump(exclude_unset=True).keys()),
        },
    )

    try:
        restaurant = await service.update_restaurant(
            restaurant_id=restaurant_id,
            update_data=data,
        )
        return restaurant

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_not_found_for_update",
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
            "api_update_restaurant_conflict",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValidationError as e:
        logger.warning(
            "api_update_restaurant_validation_error",
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
            "api_update_restaurant_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تحديث المطعم",
        )


# ==============================================
# TOGGLE RESTAURANT STATUS
# ==============================================

@router.patch(
    "/{restaurant_id}/status",
    response_model=RestaurantResponse,
    summary="تغيير حالة المطعم",
    description="تفعيل أو تعطيل مطعم",
)
async def toggle_restaurant_status(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    is_active: bool = Query(
        ...,
        description="الحالة الجديدة (true: نشط, false: غير نشط)",
    ),
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantResponse:
    """
    تفعيل أو تعطيل مطعم.
    
    Args:
        restaurant_id: معرف المطعم
        is_active: الحالة الجديدة
        service: خدمة المطاعم
        
    Returns:
        RestaurantResponse: المطعم المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على المطعم
    """
    logger.info(
        "api_toggle_restaurant_status",
        extra={
            "restaurant_id": restaurant_id,
            "is_active": is_active,
        },
    )

    try:
        restaurant = await service.toggle_restaurant_status(
            restaurant_id=restaurant_id,
            is_active=is_active,
        )
        return restaurant

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_not_found_for_status_update",
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
            "api_toggle_restaurant_status_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تغيير حالة المطعم",
        )


# ==============================================
# ACTIVATE RESTAURANT
# ==============================================

@router.post(
    "/{restaurant_id}/activate",
    response_model=RestaurantResponse,
    summary="تفعيل مطعم",
    description="تفعيل مطعم (تعيين is_active = true)",
)
async def activate_restaurant(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantResponse:
    """
    تفعيل مطعم.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة المطاعم
        
    Returns:
        RestaurantResponse: المطعم المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على المطعم
    """
    logger.info(
        "api_activate_restaurant",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        restaurant = await service.activate_restaurant(
            restaurant_id=restaurant_id,
        )
        return restaurant

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_not_found_for_activate",
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
            "api_activate_restaurant_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تفعيل المطعم",
        )


# ==============================================
# DEACTIVATE RESTAURANT
# ==============================================

@router.post(
    "/{restaurant_id}/deactivate",
    response_model=RestaurantResponse,
    summary="تعطيل مطعم",
    description="تعطيل مطعم (تعيين is_active = false)",
)
async def deactivate_restaurant(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantResponse:
    """
    تعطيل مطعم.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة المطاعم
        
    Returns:
        RestaurantResponse: المطعم المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على المطعم
    """
    logger.info(
        "api_deactivate_restaurant",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        restaurant = await service.deactivate_restaurant(
            restaurant_id=restaurant_id,
        )
        return restaurant

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_not_found_for_deactivate",
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
            "api_deactivate_restaurant_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء تعطيل المطعم",
        )


# ==============================================
# DELETE RESTAURANT
# ==============================================

@router.delete(
    "/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف مطعم",
    description="حذف مطعم موجود",
)
async def delete_restaurant(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantService = Depends(get_restaurant_service),
) -> None:
    """
    حذف مطعم.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة المطاعم
        
    Raises:
        HTTPException: إذا لم يتم العثور على المطعم أو كان يحتوي على فروع أو منتجات
    """
    logger.info(
        "api_delete_restaurant",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        await service.delete_restaurant(
            restaurant_id=restaurant_id,
        )

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_not_found_for_delete",
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
            "api_delete_restaurant_validation_error",
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
            "api_delete_restaurant_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء حذف المطعم",
        )

    logger.info(
        "api_restaurant_deleted_successfully",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# GET RESTAURANT STATS
# ==============================================

@router.get(
    "/{restaurant_id}/stats",
    response_model=RestaurantStats,
    summary="إحصائيات المطعم",
    description="الحصول على إحصائيات المطعم",
)
async def get_restaurant_stats(
    *,
    restaurant_id: int = Path(..., ge=1, description="معرف المطعم"),
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantStats:
    """
    الحصول على إحصائيات المطعم.
    
    Args:
        restaurant_id: معرف المطعم
        service: خدمة المطاعم
        
    Returns:
        RestaurantStats: إحصائيات المطعم
        
    Raises:
        HTTPException: إذا لم يتم العثور على المطعم
    """
    logger.info(
        "api_get_restaurant_stats",
        extra={"restaurant_id": restaurant_id},
    )

    try:
        stats = await service.get_restaurant_statistics(
            restaurant_id=restaurant_id,
        )
        return stats

    except NotFoundError as e:
        logger.warning(
            "api_restaurant_not_found_for_stats",
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
            "api_get_restaurant_stats_error",
            extra={
                "restaurant_id": restaurant_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب إحصائيات المطعم",
        )


# ==============================================
# GET OWNER RESTAURANTS
# ==============================================

@router.get(
    "/owner/{owner_id}",
    response_model=RestaurantListResponse,
    summary="مطاعم المالك",
    description="الحصول على مطاعم مالك معين",
)
async def get_owner_restaurants(
    *,
    owner_id: int = Path(..., ge=1, description="معرف المالك"),
    only_active: bool = Query(
        True,
        description="جلب المطاعم النشطة فقط",
    ),
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
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantListResponse:
    """
    الحصول على مطاعم مالك معين.
    
    Args:
        owner_id: معرف المالك
        only_active: جلب المطاعم النشطة فقط
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        service: خدمة المطاعم
        
    Returns:
        RestaurantListResponse: قائمة المطاعم مع الإحصائيات
    """
    logger.info(
        "api_get_owner_restaurants",
        extra={
            "owner_id": owner_id,
            "only_active": only_active,
            "skip": skip,
            "limit": limit,
        },
    )

    try:
        restaurants = await service.get_owner_restaurants(
            owner_id=owner_id,
            skip=skip,
            limit=limit,
            include_inactive=not only_active,
        )

        total = await service.count_owner_restaurants(owner_id=owner_id)

        return RestaurantListResponse(
            items=restaurants,
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.exception(
            "api_get_owner_restaurants_error",
            extra={
                "owner_id": owner_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء جلب مطاعم المالك",
        )
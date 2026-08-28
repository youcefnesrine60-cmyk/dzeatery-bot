# ==============================================
# 👤 USERS API
# نقاط نهاية API للمستخدمين
# تدير عمليات إنشاء واستعراض وتحديث وحذف المستخدمين
# ==============================================

from typing import (
    List,
    Optional,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logger import logger
from app.schemas.user import (
    ConsentResponse,
    UserConsentUpdate,
    UserCreate,
    UserResponse,
    UserSearch,
    UserSummary,
    UserUpdate,
)
from app.services.business.user_service import UserService

# ==============================================
# 🧩 TYPES
# ==============================================

UserList = List[UserResponse]

# ==============================================
# 🏗️ ROUTER
# ==============================================

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# ==============================================
# 🔧 DEPENDENCIES
# ==============================================


async def get_user_service(
    session: AsyncSession = Depends(get_db),
) -> UserService:
    """
    الحصول على خدمة المستخدمين.
    
    Args:
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        مثيل من UserService
    """
    return UserService(session)


# ==============================================
# 📋 ENDPOINTS
# ==============================================

# ==============================================
# LIST USERS
# ==============================================

@router.get(
    "/",
    response_model=UserList,
    summary="قائمة المستخدمين",
    description="الحصول على قائمة المستخدمين مع إمكانية التصفية",
)
async def list_users(
    *,
    has_consent: Optional[bool] = Query(
        None,
        description="تصفية حسب حالة الموافقة",
    ),
    search: Optional[str] = Query(
        None,
        description="نص البحث (الاسم أو رقم الهاتف)",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="عدد السجلات للتخطي",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=100,
        description="الحد الأقصى للسجلات",
    ),
    service: UserService = Depends(get_user_service),
) -> UserList:
    """
    الحصول على قائمة المستخدمين.
    
    Args:
        has_consent: تصفية حسب حالة الموافقة
        search: نص البحث
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        service: خدمة المستخدمين
        
    Returns:
        قائمة المستخدمين
    """
    logger.info(
        "api_list_users",
        extra={
            "has_consent": has_consent,
            "search": search,
            "skip": skip,
            "limit": limit,
        },
    )

    if search is not None:
        users = await service.search(
            query=search,
            skip=skip,
            limit=limit,
        )
    elif has_consent is not None:
        users = await service.get_by_consent(
            has_consent=has_consent,
            skip=skip,
            limit=limit,
        )
    else:
        users = await service.repo.get_all(
            skip=skip,
            limit=limit,
            order_by="created_at",
            descending=True,
        )

    return [
        UserResponse.model_validate(user)
        for user in users
    ]


# ==============================================
# GET USER BY ID
# ==============================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="مستخدم بالمعرف",
    description="الحصول على مستخدم محدد",
)
async def get_user(
    *,
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    الحصول على مستخدم بالمعرف.
    
    Args:
        user_id: معرف المستخدم
        service: خدمة المستخدمين
        
    Returns:
        المستخدم المطلوب
    """
    logger.info(
        "api_get_user",
        extra={"user_id": user_id},
    )

    user = await service.get_by_id(
        user_id=user_id,
    )

    if not user:
        logger.warning(
            "api_user_not_found",
            extra={"user_id": user_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


# ==============================================
# GET USER BY CHAT ID
# ==============================================

@router.get(
    "/chat/{chat_id}",
    response_model=UserResponse,
    summary="مستخدم بواسطة chat_id",
    description="الحصول على مستخدم بواسطة معرف تيليجرام",
)
async def get_user_by_chat_id(
    *,
    chat_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    الحصول على مستخدم بواسطة معرف تيليجرام.
    
    Args:
        chat_id: معرف المستخدم في تيليجرام
        service: خدمة المستخدمين
        
    Returns:
        المستخدم المطلوب
    """
    logger.info(
        "api_get_user_by_chat_id",
        extra={"chat_id": chat_id},
    )

    user = await service.get_by_chat_id(
        chat_id=chat_id,
    )

    if not user:
        logger.warning(
            "api_user_not_found_by_chat_id",
            extra={"chat_id": chat_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


# ==============================================
# CREATE USER
# ==============================================

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="إنشاء مستخدم",
    description="إنشاء مستخدم جديد",
)
async def create_user(
    *,
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    إنشاء مستخدم جديد.
    
    Args:
        data: بيانات المستخدم
        service: خدمة المستخدمين
        
    Returns:
        المستخدم المنشأ
    """
    logger.info(
        "api_create_user",
        extra={
            "chat_id": data.chat_id,
            "customer_name": data.customer_name,
        },
    )

    try:
        user = await service.create_user(
            chat_id=data.chat_id,
            consent=data.consent,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
        )

    except ValueError as e:
        logger.warning(
            "api_create_user_failed",
            extra={
                "chat_id": data.chat_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return UserResponse.model_validate(user)


# ==============================================
# UPDATE USER
# ==============================================

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="تحديث مستخدم",
    description="تحديث مستخدم موجود",
)
async def update_user(
    *,
    user_id: int,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    تحديث مستخدم موجود.
    
    Args:
        user_id: معرف المستخدم
        data: بيانات التحديث
        service: خدمة المستخدمين
        
    Returns:
        المستخدم المحدث
    """
    logger.info(
        "api_update_user",
        extra={
            "user_id": user_id,
            "fields": list(data.model_dump(exclude_unset=True).keys()),
        },
    )

    # التحقق من وجود المستخدم
    existing = await service.get_by_id(
        user_id=user_id,
    )

    if not existing:
        logger.warning(
            "api_user_not_found_for_update",
            extra={"user_id": user_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # تحديث المستخدم
    update_data = data.model_dump(exclude_unset=True)
    user = await service.repo.update(
        id=user_id,
        data=update_data,
    )

    return UserResponse.model_validate(user)


# ==============================================
# UPDATE USER CONSENT
# ==============================================

@router.patch(
    "/chat/{chat_id}/consent",
    response_model=ConsentResponse,
    summary="تحديث موافقة المستخدم",
    description="منح أو إلغاء موافقة المستخدم",
)
async def update_user_consent(
    *,
    chat_id: int,
    data: UserConsentUpdate,
    service: UserService = Depends(get_user_service),
) -> ConsentResponse:
    """
    تحديث موافقة المستخدم.
    
    Args:
        chat_id: معرف المستخدم في تيليجرام
        data: بيانات تحديث الموافقة
        service: خدمة المستخدمين
        
    Returns:
        حالة الموافقة المحدثة
    """
    logger.info(
        "api_update_user_consent",
        extra={
            "chat_id": chat_id,
            "consent": data.consent,
        },
    )

    if data.consent:
        user = await service.give_consent(
            chat_id=chat_id,
        )
        message = "User has given consent"
    else:
        user = await service.revoke_consent(
            chat_id=chat_id,
        )
        message = "User has revoked consent"

    if not user:
        logger.warning(
            "api_user_not_found_for_consent",
            extra={"chat_id": chat_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return ConsentResponse(
        chat_id=chat_id,
        has_consent=data.consent,
        message=message,
    )


# ==============================================
# CHECK USER CONSENT
# ==============================================

@router.get(
    "/chat/{chat_id}/consent",
    response_model=ConsentResponse,
    summary="التحقق من موافقة المستخدم",
    description="التحقق مما إذا كان المستخدم قد أعطى موافقته",
)
async def check_user_consent(
    *,
    chat_id: int,
    service: UserService = Depends(get_user_service),
) -> ConsentResponse:
    """
    التحقق من موافقة المستخدم.
    
    Args:
        chat_id: معرف المستخدم في تيليجرام
        service: خدمة المستخدمين
        
    Returns:
        حالة الموافقة
    """
    logger.info(
        "api_check_user_consent",
        extra={"chat_id": chat_id},
    )

    has_consent = await service.has_consent(
        chat_id=chat_id,
    )

    return ConsentResponse(
        chat_id=chat_id,
        has_consent=has_consent,
        message="User has consent" if has_consent else "User has not given consent",
    )


# ==============================================
# DELETE USER
# ==============================================

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف مستخدم",
    description="حذف مستخدم موجود",
)
async def delete_user(
    *,
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> None:
    """
    حذف مستخدم موجود.
    
    Args:
        user_id: معرف المستخدم
        service: خدمة المستخدمين
    """
    logger.info(
        "api_delete_user",
        extra={"user_id": user_id},
    )

    # التحقق من وجود المستخدم
    existing = await service.get_by_id(
        user_id=user_id,
    )

    if not existing:
        logger.warning(
            "api_user_not_found_for_delete",
            extra={"user_id": user_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    deleted = await service.repo.delete(id=user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )

    logger.info(
        "api_user_deleted_successfully",
        extra={"user_id": user_id},
    )


# ==============================================
# SEARCH USERS
# ==============================================

@router.post(
    "/search",
    response_model=UserList,
    summary="بحث عن مستخدمين",
    description="البحث عن مستخدمين بالاسم أو رقم الهاتف",
)
async def search_users(
    *,
    data: UserSearch,
    service: UserService = Depends(get_user_service),
) -> UserList:
    """
    البحث عن مستخدمين.
    
    Args:
        data: بيانات البحث
        service: خدمة المستخدمين
        
    Returns:
        قائمة المستخدمين المطابقين للبحث
    """
    logger.info(
        "api_search_users",
        extra={
            "query": data.query,
            "skip": data.skip,
            "limit": data.limit,
        },
    )

    users = await service.search(
        query=data.query,
        skip=data.skip,
        limit=data.limit,
    )

    return [
        UserResponse.model_validate(user)
        for user in users
    ]


# ==============================================
# GET USER SUMMARY
# ==============================================

@router.get(
    "/stats/summary",
    response_model=UserSummary,
    summary="ملخص المستخدمين",
    description="الحصول على ملخص إحصائيات المستخدمين",
)
async def get_user_summary(
    *,
    service: UserService = Depends(get_user_service),
) -> UserSummary:
    """
    الحصول على ملخص إحصائيات المستخدمين.
    
    Args:
        service: خدمة المستخدمين
        
    Returns:
        ملخص إحصائيات المستخدمين
    """
    logger.info("api_get_user_summary")

    stats = await service.get_user_stats()

    return UserSummary(
        total_users=stats["total_users"],
        users_with_consent=stats["users_with_consent"],
        users_without_consent=stats["users_without_consent"],
        users_with_name=stats["users_with_name"],
        users_with_phone=stats["users_with_phone"],
        consent_rate=stats["consent_rate"],
        profile_completion_rate=stats["profile_completion_rate"],
    )
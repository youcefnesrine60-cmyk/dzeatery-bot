# ==============================================
# 👑 ADMINS API
# نقاط نهاية API للمديرين
# تدير عمليات إنشاء واستعراض وتحديث وحذف المديرين
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
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.core.logger import logger
from app.schemas.admin import (
    AdminCreate,
    AdminListResponse,
    AdminLogin,
    AdminLoginResponse,
    AdminResponse,
    AdminStatistics,
    AdminUpdate,
)
from app.services.business.admin_service import AdminService

# ==============================================
# 🧩 TYPES
# ==============================================

AdminList = List[AdminResponse]

# ==============================================
# 🏗️ ROUTER
# ==============================================

router = APIRouter(
    prefix="/admins",
    tags=["Admins"],
)

# ==============================================
# 🔧 DEPENDENCIES
# ==============================================


async def get_admin_service(
    session: AsyncSession = Depends(get_db),
) -> AdminService:
    """
    الحصول على خدمة المديرين.
    
    Args:
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        مثيل من AdminService
    """
    return AdminService(session)


# ==============================================
# 🔐 AUTHENTICATION ENDPOINTS
# ==============================================

# ==============================================
# LOGIN ADMIN
# ==============================================

@router.post(
    "/login",
    response_model=AdminLoginResponse,
    summary="تسجيل دخول المدير",
    description="تسجيل دخول المدير وإنشاء جلسة جديدة",
)
async def login_admin(
    *,
    data: AdminLogin,
    service: AdminService = Depends(get_admin_service),
) -> AdminLoginResponse:
    """
    تسجيل دخول المدير.
    
    Args:
        data: بيانات تسجيل الدخول
        service: خدمة المديرين
        
    Returns:
        بيانات المدير والجلسة
        
    Raises:
        HTTPException: إذا فشل تسجيل الدخول
    """
    logger.info(
        "api_login_admin",
        extra={"username": data.username},
    )

    try:
        admin, session = await service.login(
            login_data=data,
        )

        return AdminLoginResponse(
            admin=admin,
            session=session,
        )

    except NotFoundError as e:
        logger.warning(
            "api_login_admin_not_found",
            extra={"username": data.username},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except UnauthorizedError as e:
        logger.warning(
            "api_login_admin_unauthorized",
            extra={"username": data.username},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    except Exception as e:
        logger.exception(
            "api_login_admin_failed",
            extra={
                "username": data.username,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل تسجيل الدخول، يرجى المحاولة مرة أخرى",
        )


# ==============================================
# LOGOUT ADMIN
# ==============================================

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="تسجيل خروج المدير",
    description="تسجيل خروج المدير وإلغاء تنشيط الجلسة",
)
async def logout_admin(
    *,
    session_token: str = Query(
        ...,
        description="رمز الجلسة",
    ),
    service: AdminService = Depends(get_admin_service),
) -> dict:
    """
    تسجيل خروج المدير.
    
    Args:
        session_token: رمز الجلسة
        service: خدمة المديرين
        
    Returns:
        رسالة تأكيد
    """
    logger.info(
        "api_logout_admin",
        extra={"session_token": session_token},
    )

    result = await service.logout(
        session_token=session_token,
    )

    if not result:
        logger.warning(
            "api_logout_admin_failed",
            extra={"session_token": session_token},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الجلسة غير موجودة",
        )

    return {
        "message": "تم تسجيل الخروج بنجاح",
        "success": True,
    }


# ==============================================
# VERIFY SESSION
# ==============================================

@router.post(
    "/verify",
    response_model=AdminLoginResponse,
    summary="التحقق من الجلسة",
    description="التحقق من صحة جلسة المدير",
)
async def verify_session(
    *,
    session_token: str = Query(
        ...,
        description="رمز الجلسة",
    ),
    service: AdminService = Depends(get_admin_service),
) -> AdminLoginResponse:
    """
    التحقق من صحة الجلسة.
    
    Args:
        session_token: رمز الجلسة
        service: خدمة المديرين
        
    Returns:
        بيانات المدير والجلسة
        
    Raises:
        HTTPException: إذا كانت الجلسة غير صالحة
    """
    logger.info(
        "api_verify_session",
        extra={"session_token": session_token},
    )

    result = await service.verify_session(
        session_token=session_token,
    )

    if not result:
        logger.warning(
            "api_verify_session_invalid",
            extra={"session_token": session_token},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="الجلسة غير صالحة أو منتهية الصلاحية",
        )

    admin, session = result

    return AdminLoginResponse(
        admin=admin,
        session=session,
    )


# ==============================================
# 👑 ADMIN MANAGEMENT ENDPOINTS
# ==============================================

# ==============================================
# CREATE ADMIN
# ==============================================

@router.post(
    "/",
    response_model=AdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="إنشاء مدير جديد",
    description="إنشاء مدير جديد في النظام",
)
async def create_admin(
    *,
    data: AdminCreate,
    service: AdminService = Depends(get_admin_service),
) -> AdminResponse:
    """
    إنشاء مدير جديد.
    
    Args:
        data: بيانات المدير
        service: خدمة المديرين
        
    Returns:
        المدير المنشأ
        
    Raises:
        HTTPException: إذا فشل الإنشاء
    """
    logger.info(
        "api_create_admin",
        extra={
            "username": data.username,
            "chat_id": data.chat_id,
        },
    )

    try:
        admin = await service.create_admin(
            admin_data=data,
        )

        return admin

    except ConflictError as e:
        logger.warning(
            "api_create_admin_conflict",
            extra={
                "username": data.username,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except ValidationError as e:
        logger.warning(
            "api_create_admin_validation",
            extra={
                "username": data.username,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.exception(
            "api_create_admin_failed",
            extra={
                "username": data.username,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="فشل إنشاء المدير، يرجى المحاولة مرة أخرى",
        )


# ==============================================
# GET ADMIN BY ID
# ==============================================

@router.get(
    "/{admin_id}",
    response_model=AdminResponse,
    summary="مدير بالمعرف",
    description="الحصول على مدير محدد بالمعرف",
)
async def get_admin(
    *,
    admin_id: int,
    include_inactive: bool = Query(
        False,
        description="تضمين المديرين غير النشطين",
    ),
    service: AdminService = Depends(get_admin_service),
) -> AdminResponse:
    """
    الحصول على مدير بالمعرف.
    
    Args:
        admin_id: معرف المدير
        include_inactive: تضمين المديرين غير النشطين
        service: خدمة المديرين
        
    Returns:
        المدير المطلوب
        
    Raises:
        HTTPException: إذا لم يتم العثور على المدير
    """
    logger.info(
        "api_get_admin",
        extra={
            "admin_id": admin_id,
            "include_inactive": include_inactive,
        },
    )

    try:
        admin = await service.get_admin_by_id(
            admin_id=admin_id,
            include_inactive=include_inactive,
        )

        return admin

    except NotFoundError as e:
        logger.warning(
            "api_get_admin_not_found",
            extra={"admin_id": admin_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==============================================
# GET ADMIN BY USERNAME
# ==============================================

@router.get(
    "/by-username/{username}",
    response_model=AdminResponse,
    summary="مدير باسم المستخدم",
    description="الحصول على مدير محدد باسم المستخدم",
)
async def get_admin_by_username(
    *,
    username: str,
    include_inactive: bool = Query(
        False,
        description="تضمين المديرين غير النشطين",
    ),
    service: AdminService = Depends(get_admin_service),
) -> AdminResponse:
    """
    الحصول على مدير باسم المستخدم.
    
    Args:
        username: اسم المستخدم
        include_inactive: تضمين المديرين غير النشطين
        service: خدمة المديرين
        
    Returns:
        المدير المطلوب
        
    Raises:
        HTTPException: إذا لم يتم العثور على المدير
    """
    logger.info(
        "api_get_admin_by_username",
        extra={
            "username": username,
            "include_inactive": include_inactive,
        },
    )

    try:
        admin = await service.get_admin_by_username(
            username=username,
            include_inactive=include_inactive,
        )

        return admin

    except NotFoundError as e:
        logger.warning(
            "api_get_admin_by_username_not_found",
            extra={"username": username},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==============================================
# GET ADMIN BY CHAT ID
# ==============================================

@router.get(
    "/by-chat/{chat_id}",
    response_model=AdminResponse,
    summary="مدير بمعرف الدردشة",
    description="الحصول على مدير محدد بمعرف الدردشة في Telegram",
)
async def get_admin_by_chat_id(
    *,
    chat_id: int,
    include_inactive: bool = Query(
        False,
        description="تضمين المديرين غير النشطين",
    ),
    service: AdminService = Depends(get_admin_service),
) -> AdminResponse:
    """
    الحصول على مدير بمعرف الدردشة.
    
    Args:
        chat_id: معرف الدردشة في Telegram
        include_inactive: تضمين المديرين غير النشطين
        service: خدمة المديرين
        
    Returns:
        المدير المطلوب
        
    Raises:
        HTTPException: إذا لم يتم العثور على المدير
    """
    logger.info(
        "api_get_admin_by_chat_id",
        extra={
            "chat_id": chat_id,
            "include_inactive": include_inactive,
        },
    )

    try:
        admin = await service.get_admin_by_chat_id(
            chat_id=chat_id,
            include_inactive=include_inactive,
        )

        return admin

    except NotFoundError as e:
        logger.warning(
            "api_get_admin_by_chat_id_not_found",
            extra={"chat_id": chat_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==============================================
# LIST ADMINS
# ==============================================

@router.get(
    "/",
    response_model=AdminListResponse,
    summary="قائمة المديرين",
    description="الحصول على قائمة المديرين مع إمكانية التصفية",
)
async def list_admins(
    *,
    only_active: bool = Query(
        True,
        description="جلب المديرين النشطين فقط",
    ),
    role: Optional[str] = Query(
        None,
        description="تصفية حسب الدور",
    ),
    search: Optional[str] = Query(
        None,
        description="نص البحث (username أو full_name)",
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
    order_by: str = Query(
        "id",
        description="حقل الترتيب",
    ),
    order_desc: bool = Query(
        False,
        description="ترتيب تنازلي",
    ),
    service: AdminService = Depends(get_admin_service),
) -> AdminListResponse:
    """
    الحصول على قائمة المديرين.
    
    Args:
        only_active: جلب المديرين النشطين فقط
        role: تصفية حسب الدور
        search: نص البحث
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        order_by: حقل الترتيب
        order_desc: ترتيب تنازلي
        service: خدمة المديرين
        
    Returns:
        قائمة المديرين مع الإحصائيات
    """
    logger.info(
        "api_list_admins",
        extra={
            "only_active": only_active,
            "role": role,
            "search": search,
            "skip": skip,
            "limit": limit,
        },
    )

    # البحث
    if search is not None:
        return await service.search_admins(
            query=search,
            only_active=only_active,
            skip=skip,
            limit=limit,
        )

    # تصفية حسب الدور
    if role is not None:
        return await service.get_admins_by_role(
            role=role,
            only_active=only_active,
            skip=skip,
            limit=limit,
        )

    # جلب الكل
    return await service.get_all_admins(
        only_active=only_active,
        skip=skip,
        limit=limit,
        order_by=order_by,
        order_desc=order_desc,
    )


# ==============================================
# UPDATE ADMIN
# ==============================================

@router.patch(
    "/{admin_id}",
    response_model=AdminResponse,
    summary="تحديث مدير",
    description="تحديث بيانات مدير موجود",
)
async def update_admin(
    *,
    admin_id: int,
    data: AdminUpdate,
    service: AdminService = Depends(get_admin_service),
) -> AdminResponse:
    """
    تحديث مدير موجود.
    
    Args:
        admin_id: معرف المدير
        data: بيانات التحديث
        service: خدمة المديرين
        
    Returns:
        المدير المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على المدير
    """
    logger.info(
        "api_update_admin",
        extra={
            "admin_id": admin_id,
            "fields": list(data.model_dump(exclude_unset=True).keys()),
        },
    )

    try:
        admin = await service.update_admin(
            admin_id=admin_id,
            update_data=data,
        )

        return admin

    except NotFoundError as e:
        logger.warning(
            "api_update_admin_not_found",
            extra={"admin_id": admin_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except ConflictError as e:
        logger.warning(
            "api_update_admin_conflict",
            extra={
                "admin_id": admin_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except ValidationError as e:
        logger.warning(
            "api_update_admin_validation",
            extra={
                "admin_id": admin_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


# ==============================================
# UPDATE ADMIN ROLE
# ==============================================

@router.patch(
    "/{admin_id}/role",
    response_model=AdminResponse,
    summary="تحديث دور المدير",
    description="تحديث دور مدير موجود",
)
async def update_admin_role(
    *,
    admin_id: int,
    role: str = Query(
        ...,
        description="الدور الجديد (admin, super_admin, manager)",
    ),
    service: AdminService = Depends(get_admin_service),
) -> AdminResponse:
    """
    تحديث دور المدير.
    
    Args:
        admin_id: معرف المدير
        role: الدور الجديد
        service: خدمة المديرين
        
    Returns:
        المدير المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على المدير أو كان الدور غير صالح
    """
    logger.info(
        "api_update_admin_role",
        extra={
            "admin_id": admin_id,
            "role": role,
        },
    )

    # التحقق من صحة الدور
    valid_roles = ["admin", "super_admin", "manager"]

    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"الدور يجب أن يكون أحد القيم: {', '.join(valid_roles)}",
        )

    try:
        admin = await service.update_admin_role(
            admin_id=admin_id,
            role=role,
        )

        return admin

    except NotFoundError as e:
        logger.warning(
            "api_update_admin_role_not_found",
            extra={"admin_id": admin_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==============================================
# TOGGLE ADMIN STATUS
# ==============================================

@router.patch(
    "/{admin_id}/toggle-status",
    response_model=AdminResponse,
    summary="تبديل حالة المدير",
    description="تبديل حالة المدير (نشط/غير نشط)",
)
async def toggle_admin_status(
    *,
    admin_id: int,
    service: AdminService = Depends(get_admin_service),
) -> AdminResponse:
    """
    تبديل حالة المدير.
    
    Args:
        admin_id: معرف المدير
        service: خدمة المديرين
        
    Returns:
        المدير المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على المدير
    """
    logger.info(
        "api_toggle_admin_status",
        extra={"admin_id": admin_id},
    )

    try:
        admin = await service.toggle_admin_status(
            admin_id=admin_id,
        )

        return admin

    except NotFoundError as e:
        logger.warning(
            "api_toggle_admin_status_not_found",
            extra={"admin_id": admin_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==============================================
# ACTIVATE ADMIN
# ==============================================

@router.post(
    "/{admin_id}/activate",
    response_model=AdminResponse,
    summary="تفعيل مدير",
    description="تفعيل مدير (تعيين is_active = true)",
)
async def activate_admin(
    *,
    admin_id: int,
    service: AdminService = Depends(get_admin_service),
) -> AdminResponse:
    """
    تفعيل مدير.
    
    Args:
        admin_id: معرف المدير
        service: خدمة المديرين
        
    Returns:
        المدير المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على المدير
    """
    logger.info(
        "api_activate_admin",
        extra={"admin_id": admin_id},
    )

    try:
        admin = await service.activate_admin(
            admin_id=admin_id,
        )

        return admin

    except NotFoundError as e:
        logger.warning(
            "api_activate_admin_not_found",
            extra={"admin_id": admin_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==============================================
# DEACTIVATE ADMIN
# ==============================================

@router.post(
    "/{admin_id}/deactivate",
    response_model=AdminResponse,
    summary="إلغاء تفعيل مدير",
    description="إلغاء تفعيل مدير (تعيين is_active = false)",
)
async def deactivate_admin(
    *,
    admin_id: int,
    service: AdminService = Depends(get_admin_service),
) -> AdminResponse:
    """
    إلغاء تفعيل مدير.
    
    Args:
        admin_id: معرف المدير
        service: خدمة المديرين
        
    Returns:
        المدير المحدث
        
    Raises:
        HTTPException: إذا لم يتم العثور على المدير
    """
    logger.info(
        "api_deactivate_admin",
        extra={"admin_id": admin_id},
    )

    try:
        admin = await service.deactivate_admin(
            admin_id=admin_id,
        )

        return admin

    except NotFoundError as e:
        logger.warning(
            "api_deactivate_admin_not_found",
            extra={"admin_id": admin_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==============================================
# DELETE ADMIN
# ==============================================

@router.delete(
    "/{admin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف مدير",
    description="حذف مدير موجود",
)
async def delete_admin(
    *,
    admin_id: int,
    permanent: bool = Query(
        False,
        description="حذف نهائي (بدلاً من الحذف المنطقي)",
    ),
    service: AdminService = Depends(get_admin_service),
) -> None:
    """
    حذف مدير.
    
    Args:
        admin_id: معرف المدير
        permanent: حذف نهائي
        service: خدمة المديرين
        
    Raises:
        HTTPException: إذا لم يتم العثور على المدير
    """
    logger.info(
        "api_delete_admin",
        extra={
            "admin_id": admin_id,
            "permanent": permanent,
        },
    )

    try:
        await service.delete_admin(
            admin_id=admin_id,
            permanent=permanent,
        )

        logger.info(
            "api_admin_deleted_successfully",
            extra={
                "admin_id": admin_id,
                "permanent": permanent,
            },
        )

    except NotFoundError as e:
        logger.warning(
            "api_delete_admin_not_found",
            extra={"admin_id": admin_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==============================================
# GET ADMIN STATISTICS
# ==============================================

@router.get(
    "/stats/summary",
    response_model=AdminStatistics,
    summary="إحصائيات المديرين",
    description="الحصول على إحصائيات المديرين",
)
async def get_admin_statistics(
    *,
    service: AdminService = Depends(get_admin_service),
) -> AdminStatistics:
    """
    الحصول على إحصائيات المديرين.
    
    Args:
        service: خدمة المديرين
        
    Returns:
        إحصائيات المديرين
    """
    logger.info("api_get_admin_statistics")

    stats = await service.get_admin_statistics()

    return AdminStatistics(**stats)


# ==============================================
# CHECK ADMIN PERMISSION
# ==============================================

@router.get(
    "/{admin_id}/check-permission",
    summary="التحقق من صلاحية المدير",
    description="التحقق من صلاحية مدير معين",
)
async def check_admin_permission(
    *,
    admin_id: int,
    required_role: Optional[str] = Query(
        None,
        description="الدور المطلوب",
    ),
    required_permission: Optional[str] = Query(
        None,
        description="الصلاحية المطلوبة",
    ),
    service: AdminService = Depends(get_admin_service),
) -> dict:
    """
    التحقق من صلاحية المدير.
    
    Args:
        admin_id: معرف المدير
        required_role: الدور المطلوب
        required_permission: الصلاحية المطلوبة
        service: خدمة المديرين
        
    Returns:
        نتيجة التحقق
    """
    logger.info(
        "api_check_admin_permission",
        extra={
            "admin_id": admin_id,
            "required_role": required_role,
            "required_permission": required_permission,
        },
    )

    try:
        has_permission = await service.check_admin_permission(
            admin_id=admin_id,
            required_role=required_role,
            required_permission=required_permission,
        )

        return {
            "admin_id": admin_id,
            "has_permission": has_permission,
            "required_role": required_role,
            "required_permission": required_permission,
        }

    except (NotFoundError, UnauthorizedError) as e:
        logger.warning(
            "api_check_admin_permission_failed",
            extra={
                "admin_id": admin_id,
                "error": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==============================================
# IS SUPER ADMIN
# ==============================================

@router.get(
    "/{admin_id}/is-super-admin",
    summary="التحقق من مشرف عام",
    description="التحقق من أن المدير هو مشرف عام",
)
async def is_super_admin(
    *,
    admin_id: int,
    service: AdminService = Depends(get_admin_service),
) -> dict:
    """
    التحقق من أن المدير هو مشرف عام.
    
    Args:
        admin_id: معرف المدير
        service: خدمة المديرين
        
    Returns:
        نتيجة التحقق
    """
    logger.info(
        "api_is_super_admin",
        extra={"admin_id": admin_id},
    )

    result = await service.is_super_admin(
        admin_id=admin_id,
    )

    return {
        "admin_id": admin_id,
        "is_super_admin": result,
    }
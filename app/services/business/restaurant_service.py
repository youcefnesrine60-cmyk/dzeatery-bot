# ==============================================
# 🏪 RESTAURANT SERVICE
# منطق الأعمال للمطاعم
# يدير عمليات إنشاء واستعراض وتحديث وحذف المطاعم
# ==============================================

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from sqlalchemy.ext.asyncio import AsyncSession

# ✅ استيراد الاستثناءات
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

# ✅ استيراد دوال الأمان
from app.core.security import (
    sanitize_input,
)

from app.core.logger import logger
from app.models.restaurant import Restaurant
from app.repositories.restaurant_repo import RestaurantRepository

# ✅ استيراد المخططات
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate,
    RestaurantStats,
)

# ==============================================
# 🧩 CONSTANTS
# ==============================================

MAX_RESTAURANTS_PER_OWNER = 5
VALID_RESTAURANT_TYPES = {"restaurant", "cafe", "fast_food", "bakery", "pizza", "other"}


# ==============================================
# 🧩 TYPES
# ==============================================

RestaurantData = Dict[str, Any]
RestaurantUpdateData = Dict[str, Any]
RestaurantList = List[Restaurant]


# ==============================================
# 🏪 RESTAURANT SERVICE
# ==============================================


class RestaurantService:
    """
    خدمة المطاعم - تدير منطق الأعمال للمطاعم.
    
    مسؤولة عن:
        - إنشاء وإدارة المطاعم
        - البحث والتصفية
        - تحديث حالة المطاعم
        - حذف المطاعم
    
    Attributes:
        session: جلسة قاعدة البيانات غير المتزامنة
        repo: مستودع المطاعم
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        تهيئة خدمة المطاعم.
        
        Args:
            session: جلسة قاعدة البيانات غير المتزامنة
        """
        self.session = session
        self.repo = RestaurantRepository(session)

    # ==========================================
    # 📖 QUERIES
    # ==========================================

    # ==============================================
    # GET RESTAURANT
    # ==============================================

    async def get_restaurant(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantResponse:
        """
        الحصول على مطعم بالمعرف.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantResponse: بيانات المطعم
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المطعم
        """
        logger.info(
            "restaurant_service_get_by_id",
            extra={"restaurant_id": restaurant_id},
        )

        restaurant = await self.repo.get_by_id(
            restaurant_id=restaurant_id,
        )

        if not restaurant:
            raise NotFoundError(
                message=f"المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        return RestaurantResponse.model_validate(restaurant)

    # ==============================================
    # GET RESTAURANT WITH DETAILS
    # ==============================================

    async def get_restaurant_with_details(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantResponse:
        """
        الحصول على مطعم مع جميع علاقاته.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantResponse: بيانات المطعم مع العلاقات
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المطعم
        """
        logger.info(
            "restaurant_service_get_with_details",
            extra={"restaurant_id": restaurant_id},
        )

        restaurant = await self.repo.get_with_relations(
            restaurant_id=restaurant_id,
        )

        if not restaurant:
            raise NotFoundError(
                message=f"المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        return RestaurantResponse.model_validate(restaurant)

    # ==============================================
    # GET OWNER RESTAURANTS
    # ==============================================

    async def get_owner_restaurants(
        self,
        *,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> List[RestaurantResponse]:
        """
        الحصول على مطاعم المالك.
        
        Args:
            owner_id: معرف المالك
            skip: عدد السجلات للتخطي
            limit: الحد الأقصى للسجلات
            include_inactive: تضمين المطاعم غير النشطة
            
        Returns:
            List[RestaurantResponse]: قائمة المطاعم
        """
        logger.info(
            "restaurant_service_get_by_owner",
            extra={
                "owner_id": owner_id,
                "skip": skip,
                "limit": limit,
            },
        )

        restaurants = await self.repo.get_by_owner_id(
            owner_id=owner_id,
            skip=skip,
            limit=limit,
            include_inactive=include_inactive,
        )

        return [RestaurantResponse.model_validate(r) for r in restaurants]

    # ==============================================
    # GET RESTAURANTS BY WILAYA
    # ==============================================

    async def get_restaurants_by_wilaya(
        self,
        *,
        wilaya: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RestaurantResponse]:
        """
        الحصول على مطاعم حسب الولاية.
        
        Args:
            wilaya: الولاية
            skip: عدد السجلات للتخطي
            limit: الحد الأقصى للسجلات
            
        Returns:
            List[RestaurantResponse]: قائمة المطاعم
        """
        clean_wilaya = sanitize_input(wilaya)

        logger.info(
            "restaurant_service_get_by_wilaya",
            extra={
                "wilaya": clean_wilaya,
                "skip": skip,
                "limit": limit,
            },
        )

        restaurants = await self.repo.get_by_wilaya(
            wilaya=clean_wilaya,
            skip=skip,
            limit=limit,
        )

        return [RestaurantResponse.model_validate(r) for r in restaurants]

    # ==============================================
    # SEARCH RESTAURANTS
    # ==============================================

    async def search_restaurants(
        self,
        *,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RestaurantResponse]:
        """
        البحث عن مطاعم.
        
        Args:
            query: نص البحث
            skip: عدد السجلات للتخطي
            limit: الحد الأقصى للسجلات
            
        Returns:
            List[RestaurantResponse]: قائمة المطاعم المطابقة للبحث
        """
        clean_query = sanitize_input(query)

        logger.info(
            "restaurant_service_search",
            extra={
                "query": clean_query,
                "skip": skip,
                "limit": limit,
            },
        )

        restaurants = await self.repo.search(
            query=clean_query,
            skip=skip,
            limit=limit,
        )

        return [RestaurantResponse.model_validate(r) for r in restaurants]

    # ==============================================
    # GET ALL RESTAURANTS
    # ==============================================

    async def get_all_restaurants(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = True,
    ) -> List[RestaurantResponse]:
        """
        الحصول على جميع المطاعم.
        
        Args:
            skip: عدد السجلات للتخطي
            limit: الحد الأقصى للسجلات
            only_active: جلب المطاعم النشطة فقط
            
        Returns:
            List[RestaurantResponse]: قائمة المطاعم
        """
        logger.info(
            "restaurant_service_get_all",
            extra={
                "skip": skip,
                "limit": limit,
                "only_active": only_active,
            },
        )

        filters = {}
        if only_active:
            filters["is_active"] = True

        restaurants = await self.repo.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="name",
        )

        return [RestaurantResponse.model_validate(r) for r in restaurants]

    # ==========================================
    # 📊 STATISTICS
    # ==========================================

    # ==============================================
    # COUNT OWNER RESTAURANTS
    # ==============================================

    async def count_owner_restaurants(
        self,
        *,
        owner_id: int,
    ) -> int:
        """
        حساب عدد مطاعم المالك.
        
        Args:
            owner_id: معرف المالك
            
        Returns:
            int: عدد المطاعم
        """
        return await self.repo.count_by_owner(owner_id=owner_id)

    # ==============================================
    # COUNT RESTAURANTS BY WILAYA
    # ==============================================

    async def count_restaurants_by_wilaya(
        self,
        *,
        wilaya: str,
    ) -> int:
        """
        حساب عدد المطاعم في الولاية.
        
        Args:
            wilaya: الولاية
            
        Returns:
            int: عدد المطاعم
        """
        clean_wilaya = sanitize_input(wilaya)

        return await self.repo.count_by_wilaya(wilaya=clean_wilaya)

    # ==============================================
    # GET RESTAURANT STATISTICS
    # ==============================================

    async def get_restaurant_statistics(
        self,
        *,
        owner_id: Optional[int] = None,
    ) -> RestaurantStats:
        """
        الحصول على إحصائيات المطاعم.
        
        Args:
            owner_id: معرف المالك (اختياري)
            
        Returns:
            RestaurantStats: إحصائيات المطاعم
        """
        logger.info(
            "restaurant_service_get_statistics",
            extra={"owner_id": owner_id},
        )

        filters = {}
        if owner_id:
            filters["owner_id"] = owner_id

        all_restaurants = await self.repo.get_all(
            filters=filters,
            limit=10000,
        )

        total = len(all_restaurants)
        active = len([r for r in all_restaurants if r.is_active])
        inactive = total - active

        # توزيع المطاعم حسب النوع
        type_distribution: Dict[str, int] = {}

        for restaurant in all_restaurants:
            rest_type = restaurant.type or "unknown"
            type_distribution[rest_type] = type_distribution.get(rest_type, 0) + 1

        # توزيع المطاعم حسب الولاية
        wilaya_distribution: Dict[str, int] = {}

        for restaurant in all_restaurants:
            wilaya = restaurant.wilaya or "unknown"
            wilaya_distribution[wilaya] = wilaya_distribution.get(wilaya, 0) + 1

        return RestaurantStats(
            total_restaurants=total,
            active_restaurants=active,
            inactive_restaurants=inactive,
            type_distribution=type_distribution,
            wilaya_distribution=wilaya_distribution,
        )

    # ==========================================
    # ✏️ MUTATIONS
    # ==========================================

    # ==============================================
    # CREATE RESTAURANT
    # ==============================================

    async def create_restaurant(
        self,
        *,
        restaurant_data: RestaurantCreate,
    ) -> RestaurantResponse:
        """
        إنشاء مطعم جديد.
        
        Args:
            restaurant_data: بيانات المطعم
            
        Returns:
            RestaurantResponse: بيانات المطعم المنشأ
            
        Raises:
            ConflictError: إذا كان الاسم موجوداً مسبقاً لنفس المالك
            ValidationError: إذا كانت البيانات غير صالحة
            UnauthorizedError: إذا تجاوز المالك الحد الأقصى للمطاعم
        """
        # تنظيف البيانات
        name = sanitize_input(restaurant_data.name)
        wilaya = sanitize_input(restaurant_data.wilaya) if restaurant_data.wilaya else None

        logger.info(
            "restaurant_service_create",
            extra={
                "owner_id": restaurant_data.owner_id,
                "restaurant_name": name,
                "type": restaurant_data.type,
                "wilaya": wilaya,
            },
        )

        # التحقق من صحة نوع المطعم
        if restaurant_data.type not in VALID_RESTAURANT_TYPES:
            raise ValidationError(
                message=f"نوع المطعم '{restaurant_data.type}' غير صالح",
                details={
                    "type": restaurant_data.type,
                    "valid_types": list(VALID_RESTAURANT_TYPES),
                },
            )

        # التحقق من الحد الأقصى للمطاعم لكل مالك
        current_count = await self.count_owner_restaurants(
            owner_id=restaurant_data.owner_id,
        )

        if current_count >= MAX_RESTAURANTS_PER_OWNER:
            raise UnauthorizedError(
                message=f"تجاوزت الحد الأقصى للمطاعم ({MAX_RESTAURANTS_PER_OWNER})",
                details={
                    "owner_id": restaurant_data.owner_id,
                    "current_count": current_count,
                    "max_allowed": MAX_RESTAURANTS_PER_OWNER,
                },
            )

        # التحقق من عدم وجود مطعم بنفس الاسم لنفس المالك
        existing = await self.repo.get_by_name_and_owner(
            owner_id=restaurant_data.owner_id,
            name=name,
        )

        if existing:
            raise ConflictError(
                message=f"يوجد مطعم باسم '{name}' بالفعل لهذا المالك",
            )

        # إنشاء المطعم
        data: RestaurantData = {
            "owner_id": restaurant_data.owner_id,
            "name": name,
            "type": restaurant_data.type,
            "phone": restaurant_data.phone,
            "wilaya": wilaya,
            "lat": restaurant_data.lat,
            "lng": restaurant_data.lng,
            "group_id": restaurant_data.group_id,
            "is_active": restaurant_data.is_active if restaurant_data.is_active is not None else True,
        }

        restaurant = await self.repo.create(data=data)

        logger.info(
            "restaurant_created_successfully",
            extra={
                "restaurant_id": restaurant.id,
                "restaurant_name": restaurant.name,
            },
        )

        return RestaurantResponse.model_validate(restaurant)

    # ==============================================
    # UPDATE RESTAURANT
    # ==============================================

    async def update_restaurant(
        self,
        *,
        restaurant_id: int,
        update_data: RestaurantUpdate,
    ) -> RestaurantResponse:
        """
        تحديث مطعم.
        
        Args:
            restaurant_id: معرف المطعم
            update_data: بيانات التحديث
            
        Returns:
            RestaurantResponse: بيانات المطعم المحدث
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المطعم
            ConflictError: إذا كان الاسم موجوداً مسبقاً
            ValidationError: إذا كانت البيانات غير صالحة
        """
        logger.info(
            "restaurant_service_update",
            extra={
                "restaurant_id": restaurant_id,
                "fields": list(update_data.model_dump(exclude_unset=True).keys()),
            },
        )

        # التحقق من وجود المطعم
        existing = await self.repo.get_by_id(
            restaurant_id=restaurant_id,
        )

        if not existing:
            raise NotFoundError(
                message=f"المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        # تحضير بيانات التحديث
        updates = update_data.model_dump(exclude_unset=True)

        # تنظيف البيانات
        if "name" in updates:
            updates["name"] = sanitize_input(updates["name"])

            # التحقق من عدم وجود اسم مكرر لنفس المالك
            duplicate = await self.repo.get_by_name_and_owner(
                owner_id=existing.owner_id,
                name=updates["name"],
            )

            if duplicate and duplicate.id != restaurant_id:
                raise ConflictError(
                    message=f"يوجد مطعم باسم '{updates['name']}' بالفعل لهذا المالك",
                )

        if "wilaya" in updates:
            updates["wilaya"] = sanitize_input(updates["wilaya"]) if updates["wilaya"] else None

        if "type" in updates and updates["type"] not in VALID_RESTAURANT_TYPES:
            raise ValidationError(
                message=f"نوع المطعم '{updates['type']}' غير صالح",
                details={
                    "type": updates["type"],
                    "valid_types": list(VALID_RESTAURANT_TYPES),
                },
            )

        # تحديث المطعم
        restaurant = await self.repo.update(
            restaurant_id=restaurant_id,
            data=updates,
        )

        if not restaurant:
            raise NotFoundError(
                message=f"المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        logger.info(
            "restaurant_updated_successfully",
            extra={
                "restaurant_id": restaurant_id,
                "updated_fields": list(updates.keys()),
            },
        )

        return RestaurantResponse.model_validate(restaurant)

    # ==============================================
    # TOGGLE RESTAURANT STATUS
    # ==============================================

    async def toggle_restaurant_status(
        self,
        *,
        restaurant_id: int,
        is_active: bool,
    ) -> RestaurantResponse:
        """
        تفعيل/تعطيل مطعم.
        
        Args:
            restaurant_id: معرف المطعم
            is_active: الحالة الجديدة
            
        Returns:
            RestaurantResponse: بيانات المطعم المحدث
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المطعم
        """
        logger.info(
            "restaurant_service_toggle_status",
            extra={
                "restaurant_id": restaurant_id,
                "is_active": is_active,
            },
        )

        restaurant = await self.repo.update_status(
            restaurant_id=restaurant_id,
            is_active=is_active,
        )

        if not restaurant:
            raise NotFoundError(
                message=f"المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        logger.info(
            "restaurant_status_toggled_successfully",
            extra={
                "restaurant_id": restaurant_id,
                "is_active": is_active,
            },
        )

        return RestaurantResponse.model_validate(restaurant)

    # ==============================================
    # ACTIVATE RESTAURANT
    # ==============================================

    async def activate_restaurant(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantResponse:
        """
        تفعيل مطعم.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantResponse: بيانات المطعم المحدث
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المطعم
        """
        logger.info(
            "restaurant_service_activate",
            extra={"restaurant_id": restaurant_id},
        )

        return await self.toggle_restaurant_status(
            restaurant_id=restaurant_id,
            is_active=True,
        )

    # ==============================================
    # DEACTIVATE RESTAURANT
    # ==============================================

    async def deactivate_restaurant(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantResponse:
        """
        تعطيل مطعم.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantResponse: بيانات المطعم المحدث
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المطعم
        """
        logger.info(
            "restaurant_service_deactivate",
            extra={"restaurant_id": restaurant_id},
        )

        return await self.toggle_restaurant_status(
            restaurant_id=restaurant_id,
            is_active=False,
        )

    # ==============================================
    # DELETE RESTAURANT
    # ==============================================

    async def delete_restaurant(
        self,
        *,
        restaurant_id: int,
    ) -> None:
        """
        حذف مطعم.
        
        Args:
            restaurant_id: معرف المطعم
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المطعم
            ValidationError: إذا كان المطعم يحتوي على فروع أو منتجات
        """
        logger.info(
            "restaurant_service_delete",
            extra={"restaurant_id": restaurant_id},
        )

        # التحقق من وجود المطعم
        restaurant = await self.repo.get_by_id(
            restaurant_id=restaurant_id,
        )

        if not restaurant:
            raise NotFoundError(
                message=f"المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        # التحقق من وجود فروع تابعة
        branches_count = await self.repo.count_branches(restaurant_id=restaurant_id)

        if branches_count > 0:
            raise ValidationError(
                message="لا يمكن حذف المطعم لأنه يحتوي على فروع",
                details={
                    "restaurant_id": restaurant_id,
                    "branches_count": branches_count,
                },
            )

        # التحقق من وجود منتجات
        products_count = await self.repo.count_products(restaurant_id=restaurant_id)

        if products_count > 0:
            raise ValidationError(
                message="لا يمكن حذف المطعم لأنه يحتوي على منتجات",
                details={
                    "restaurant_id": restaurant_id,
                    "products_count": products_count,
                },
            )

        # حذف المطعم
        deleted = await self.repo.delete(restaurant_id=restaurant_id)

        if not deleted:
            raise NotFoundError(
                message=f"المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        logger.info(
            "restaurant_deleted_successfully",
            extra={"restaurant_id": restaurant_id},
        )


# ==============================================
# 🔄 COMPATIBILITY FUNCTIONS
# دوال متوافقة مع الاستيرادات القديمة
# ==============================================

# ==============================================
# CREATE RESTAURANT (COMPATIBILITY)
# ==============================================

async def create_restaurant(
    *,
    owner_id: int,
    name: str,
    type: str,
    phone: str,
    wilaya: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    group_id: Optional[int] = None,
    is_active: bool = True,
    session: AsyncSession,
) -> int:
    """
    إنشاء مطعم جديد (دالة متوافقة مع الإصدار القديم).
    
    Args:
        owner_id: معرف المالك
        name: اسم المطعم
        type: نوع المطعم
        phone: رقم الهاتف
        wilaya: الولاية
        lat: خط العرض
        lng: خط الطول
        group_id: معرف المجموعة
        is_active: حالة النشاط
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        int: معرف المطعم
        
    Raises:
        ConflictError: إذا كان الاسم موجوداً مسبقاً
        ValidationError: إذا كانت البيانات غير صالحة
        UnauthorizedError: إذا تجاوز المالك الحد الأقصى
    """
    service = RestaurantService(session=session)

    restaurant_data = RestaurantCreate(
        owner_id=owner_id,
        name=name,
        type=type,
        phone=phone,
        wilaya=wilaya,
        lat=lat,
        lng=lng,
        group_id=group_id,
        is_active=is_active,
    )

    restaurant = await service.create_restaurant(
        restaurant_data=restaurant_data,
    )

    return restaurant.id


# ==============================================
# GET RESTAURANT (COMPATIBILITY)
# ==============================================

async def get_restaurant(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> Optional[Dict[str, Any]]:
    """
    الحصول على مطعم بالمعرف (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        Optional[Dict[str, Any]]: قاموس بيانات المطعم أو None
    """
    service = RestaurantService(session=session)

    try:
        restaurant = await service.get_restaurant(restaurant_id=restaurant_id)
        return restaurant.model_dump()
    except NotFoundError:
        return None


# ==============================================
# GET RESTAURANTS (COMPATIBILITY)
# ==============================================

async def get_restaurants(
    *,
    owner_id: int,
    session: AsyncSession,
    include_inactive: bool = False,
) -> List[Dict[str, Any]]:
    """
    الحصول على مطاعم المالك (دالة متوافقة مع الإصدار القديم).
    
    Args:
        owner_id: معرف المالك
        session: جلسة قاعدة البيانات غير المتزامنة
        include_inactive: تضمين المطاعم غير النشطة
        
    Returns:
        List[Dict[str, Any]]: قائمة المطاعم
    """
    service = RestaurantService(session=session)

    restaurants = await service.get_owner_restaurants(
        owner_id=owner_id,
        include_inactive=include_inactive,
    )

    return [r.model_dump() for r in restaurants]


# ==============================================
# GET ALL RESTAURANTS (COMPATIBILITY)
# ==============================================

async def get_all_restaurants(
    *,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    only_active: bool = True,
) -> List[Dict[str, Any]]:
    """
    الحصول على جميع المطاعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        session: جلسة قاعدة البيانات غير المتزامنة
        skip: عدد السجلات للتخطي
        limit: الحد الأقصى للسجلات
        only_active: جلب المطاعم النشطة فقط
        
    Returns:
        List[Dict[str, Any]]: قائمة المطاعم
    """
    service = RestaurantService(session=session)

    restaurants = await service.get_all_restaurants(
        skip=skip,
        limit=limit,
        only_active=only_active,
    )

    return [r.model_dump() for r in restaurants]


# ==============================================
# UPDATE RESTAURANT (COMPATIBILITY)
# ==============================================

async def update_restaurant(
    *,
    restaurant_id: int,
    data: RestaurantUpdateData,
    session: AsyncSession,
) -> None:
    """
    تحديث مطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        data: بيانات التحديث
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المطعم
        ConflictError: إذا كان الاسم موجوداً مسبقاً
        ValidationError: إذا كانت البيانات غير صالحة
    """
    service = RestaurantService(session=session)

    update_data = RestaurantUpdate(**data)

    await service.update_restaurant(
        restaurant_id=restaurant_id,
        update_data=update_data,
    )

    logger.info(
        "restaurant_updated",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# DELETE RESTAURANT (COMPATIBILITY)
# ==============================================

async def delete_restaurant(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    حذف مطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المطعم
        ValidationError: إذا كان المطعم يحتوي على فروع أو منتجات
    """
    service = RestaurantService(session=session)

    await service.delete_restaurant(restaurant_id=restaurant_id)

    logger.info(
        "restaurant_deleted",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# TOGGLE RESTAURANT STATUS (COMPATIBILITY)
# ==============================================

async def toggle_restaurant_status(
    *,
    restaurant_id: int,
    is_active: bool,
    session: AsyncSession,
) -> None:
    """
    تفعيل/تعطيل مطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        is_active: الحالة الجديدة
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المطعم
    """
    service = RestaurantService(session=session)

    await service.toggle_restaurant_status(
        restaurant_id=restaurant_id,
        is_active=is_active,
    )

    logger.info(
        "restaurant_status_toggled",
        extra={
            "restaurant_id": restaurant_id,
            "is_active": is_active,
        },
    )
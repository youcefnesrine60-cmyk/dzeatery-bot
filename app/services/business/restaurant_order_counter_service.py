# ==============================================
# 🔢 RESTAURANT ORDER COUNTER SERVICE
# منطق الأعمال لعداد طلبات المطعم
#
# إنشاء عداد طلبات
# قراءة عداد طلبات
# تحديث عداد طلبات
# زيادة عداد طلبات
# توليد رقم طلب
# إعادة تعيين عداد طلبات
# ==============================================

from typing import (
    Any,
    Dict,
    Optional,
)

from sqlalchemy.ext.asyncio import AsyncSession

# ✅ استيراد الاستثناءات
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)

from app.core.logger import logger
from app.models.restaurant_order_counter import RestaurantOrderCounter
from app.repositories.restaurant_order_counters_repo import (
    RestaurantOrderCountersRepository,
)
from app.repositories.restaurant_repo import RestaurantRepository

# ✅ استيراد المخططات
from app.schemas.restaurant_order_counter import (
    RestaurantOrderCounterResponse,
    RestaurantOrderCounterUpdate,
    NextOrderNumberResponse,
    OrderCounterSummary,
)


# ==============================================
# 🧩 TYPES
# ==============================================

OrderCounterData = Dict[str, Any]
OrderCounterUpdateData = Dict[str, Any]
CounterSummary = Dict[str, Any]


# ==============================================
# 🔢 RESTAURANT ORDER COUNTER SERVICE
# ==============================================


class RestaurantOrderCounterService:
    """
    خدمة عداد طلبات المطعم - تدير منطق الأعمال لعداد الطلبات.
    
    مسؤولة عن:
        - إنشاء عداد طلبات
        - قراءة عداد طلبات
        - تحديث عداد طلبات
        - زيادة عداد طلبات
        - توليد رقم طلب
        - إعادة تعيين عداد طلبات
    
    Attributes:
        session: جلسة قاعدة البيانات غير المتزامنة
        repo: مستودع عداد الطلبات
        restaurant_repo: مستودع المطاعم
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        تهيئة خدمة عداد طلبات المطعم.
        
        Args:
            session: جلسة قاعدة البيانات غير المتزامنة
        """
        self.session = session
        self.repo = RestaurantOrderCountersRepository(session)
        self.restaurant_repo = RestaurantRepository(session)

    # ==========================================
    # 📖 QUERIES
    # ==========================================

    # ==============================================
    # GET COUNTER
    # ==============================================

    async def get_counter(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantOrderCounterResponse:
        """
        الحصول على عداد طلبات مطعم معين.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantOrderCounterResponse: بيانات عداد الطلبات
            
        Raises:
            NotFoundError: إذا لم يتم العثور على العداد
        """
        logger.info(
            "order_counter_service_get_counter",
            extra={"restaurant_id": restaurant_id},
        )

        counter = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not counter:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        return RestaurantOrderCounterResponse.model_validate(counter)

    # ==============================================
    # GET CURRENT NUMBER
    # ==============================================

    async def get_current_number(
        self,
        *,
        restaurant_id: int,
    ) -> int:
        """
        الحصول على رقم الطلب الحالي لمطعم معين.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            int: آخر رقم طلب
            
        Raises:
            NotFoundError: إذا لم يتم العثور على العداد
        """
        logger.info(
            "order_counter_service_get_current_number",
            extra={"restaurant_id": restaurant_id},
        )

        number = await self.repo.get_current_number(
            restaurant_id=restaurant_id,
        )

        if number < 0:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        return number

    # ==============================================
    # GET NEXT ORDER NUMBER
    # ==============================================

    async def get_next_order_number(
        self,
        *,
        restaurant_id: int,
    ) -> NextOrderNumberResponse:
        """
        الحصول على رقم الطلب التالي لمطعم معين.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            NextOrderNumberResponse: رقم الطلب التالي
            
        Raises:
            NotFoundError: إذا لم يتم العثور على العداد
        """
        logger.info(
            "order_counter_service_get_next_order_number",
            extra={"restaurant_id": restaurant_id},
        )

        counter = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not counter:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        next_number = counter.last_number + 1
        formatted_number = self.build_order_number(
            restaurant_id=restaurant_id,
            sequence=next_number,
        )

        return NextOrderNumberResponse(
            restaurant_id=restaurant_id,
            next_number=next_number,
            formatted_number=formatted_number,
        )

    # ==========================================
    # 📊 STATISTICS
    # ==========================================

    # ==============================================
    # GET COUNTER SUMMARY
    # ==============================================

    async def get_counter_summary(
        self,
        *,
        restaurant_id: int,
    ) -> OrderCounterSummary:
        """
        الحصول على ملخص عداد طلبات مطعم.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            OrderCounterSummary: ملخص العداد
        """
        logger.info(
            "order_counter_service_get_summary",
            extra={"restaurant_id": restaurant_id},
        )

        counter = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not counter:
            return OrderCounterSummary(
                restaurant_id=restaurant_id,
                exists=False,
                total_orders=0,
                last_order_number=None,
                next_order_number=None,
            )

        last_order_number = self.build_order_number(
            restaurant_id=restaurant_id,
            sequence=counter.last_number,
        )

        next_order_number = self.build_order_number(
            restaurant_id=restaurant_id,
            sequence=counter.last_number + 1,
        )

        return OrderCounterSummary(
            restaurant_id=restaurant_id,
            exists=True,
            total_orders=counter.last_number,
            last_order_number=last_order_number,
            next_order_number=next_order_number,
        )

    # ==========================================
    # ✏️ MUTATIONS
    # ==========================================

    # ==============================================
    # INITIALIZE COUNTER
    # ==============================================

    async def initialize_counter(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantOrderCounterResponse:
        """
        تهيئة عداد طلبات جديد لمطعم.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantOrderCounterResponse: بيانات العداد المنشأ
            
        Raises:
            NotFoundError: إذا لم يتم العثور على المطعم
            ConflictError: إذا كان العداد موجوداً مسبقاً
        """
        logger.info(
            "order_counter_service_initialize",
            extra={"restaurant_id": restaurant_id},
        )

        # التحقق من وجود المطعم
        restaurant = await self.restaurant_repo.get_by_id(
            id=restaurant_id,
        )

        if not restaurant:
            raise NotFoundError(
                message=f"المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        # التحقق من عدم وجود عداد مسبق
        existing = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if existing:
            raise ConflictError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' موجود مسبقاً",
            )

        # إنشاء عداد جديد
        counter = await self.repo.create_counter(
            restaurant_id=restaurant_id,
        )

        logger.info(
            "order_counter_service_initialized_successfully",
            extra={
                "restaurant_id": restaurant_id,
                "counter_id": counter.restaurant_id,
            },
        )

        return RestaurantOrderCounterResponse.model_validate(counter)

    # ==============================================
    # UPDATE COUNTER
    # ==============================================

    async def update_counter(
        self,
        *,
        restaurant_id: int,
        update_data: RestaurantOrderCounterUpdate,
    ) -> RestaurantOrderCounterResponse:
        """
        تحديث عداد طلبات مطعم.
        
        Args:
            restaurant_id: معرف المطعم
            update_data: بيانات التحديث
            
        Returns:
            RestaurantOrderCounterResponse: بيانات العداد المحدث
            
        Raises:
            NotFoundError: إذا لم يتم العثور على العداد
            ValidationError: إذا كانت البيانات غير صالحة
        """
        logger.info(
            "order_counter_service_update",
            extra={
                "restaurant_id": restaurant_id,
                "fields": list(update_data.model_dump(exclude_unset=True).keys()),
            },
        )

        # التحقق من وجود العداد
        counter = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not counter:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        updates = update_data.model_dump(exclude_unset=True)

        # التحقق من صحة القيمة
        if "last_number" in updates:
            if updates["last_number"] < 0:
                raise ValidationError(
                    message="رقم الطلب لا يمكن أن يكون سالباً",
                )

        # تحديث العداد
        updated = await self.repo.update(
            id=counter.restaurant_id,
            data=updates,
        )

        if not updated:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        logger.info(
            "order_counter_service_updated_successfully",
            extra={"restaurant_id": restaurant_id},
        )

        return RestaurantOrderCounterResponse.model_validate(updated)

    # ==============================================
    # INCREMENT COUNTER
    # ==============================================

    async def increment_counter(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantOrderCounterResponse:
        """
        زيادة عداد طلبات مطعم بمقدار 1.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantOrderCounterResponse: بيانات العداد المحدث
            
        Raises:
            NotFoundError: إذا لم يتم العثور على العداد
        """
        logger.info(
            "order_counter_service_increment",
            extra={"restaurant_id": restaurant_id},
        )

        # التحقق من وجود العداد
        counter = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not counter:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        # زيادة العداد
        await self.repo.increment_counter(
            restaurant_id=restaurant_id,
        )

        # جلب العداد المحدث
        updated = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not updated:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        logger.info(
            "order_counter_service_incremented_successfully",
            extra={
                "restaurant_id": restaurant_id,
                "new_number": updated.last_number,
            },
        )

        return RestaurantOrderCounterResponse.model_validate(updated)

    # ==============================================
    # RESET COUNTER
    # ==============================================

    async def reset_counter(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantOrderCounterResponse:
        """
        إعادة تعيين عداد طلبات مطعم إلى الصفر.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantOrderCounterResponse: بيانات العداد المعاد تعيينه
            
        Raises:
            NotFoundError: إذا لم يتم العثور على العداد
        """
        logger.info(
            "order_counter_service_reset",
            extra={"restaurant_id": restaurant_id},
        )

        # التحقق من وجود العداد
        counter = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not counter:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        # إعادة تعيين العداد
        updated = await self.repo.update(
            id=counter.restaurant_id,
            data={"last_number": 0},
        )

        if not updated:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        logger.info(
            "order_counter_service_reset_successfully",
            extra={"restaurant_id": restaurant_id},
        )

        return RestaurantOrderCounterResponse.model_validate(updated)

    # ==============================================
    # GENERATE NEXT ORDER NUMBER
    # ==============================================

    async def generate_next_order_number(
        self,
        *,
        restaurant_id: int,
    ) -> NextOrderNumberResponse:
        """
        توليد رقم الطلب التالي لمطعم (يزيد العداد ويعيد الرقم المنسق).
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            NextOrderNumberResponse: رقم الطلب التالي
            
        Raises:
            NotFoundError: إذا لم يتم العثور على العداد
        """
        logger.info(
            "order_counter_service_generate_next",
            extra={"restaurant_id": restaurant_id},
        )

        # التحقق من وجود العداد
        counter = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not counter:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        # توليد الرقم التالي (يزيد العداد تلقائياً)
        order_number = await self.repo.generate_next_order_number(
            restaurant_id=restaurant_id,
        )

        logger.info(
            "order_counter_service_generated_successfully",
            extra={
                "restaurant_id": restaurant_id,
                "order_number": order_number,
            },
        )

        # الحصول على الرقم الحالي
        updated = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not updated:
            raise NotFoundError(
                message=f"عداد طلبات المطعم بـ ID '{restaurant_id}' غير موجود",
            )

        return NextOrderNumberResponse(
            restaurant_id=restaurant_id,
            next_number=updated.last_number,
            formatted_number=order_number,
        )

    # ==========================================
    # 🏷️ HELPERS
    # ==========================================

    # ==============================================
    # BUILD ORDER NUMBER
    # ==============================================

    @staticmethod
    def build_order_number(
        restaurant_id: int,
        sequence: int,
    ) -> str:
        """
        بناء رقم طلب منسق.
        
        Args:
            restaurant_id: معرف المطعم
            sequence: رقم التسلسل
            
        Returns:
            str: رقم الطلب المنسق
        """
        return RestaurantOrderCountersRepository.build_order_number(
            restaurant_id=restaurant_id,
            sequence=sequence,
        )

    # ==============================================
    # VALIDATE ORDER NUMBER FORMAT
    # ==============================================

    @staticmethod
    def validate_order_number_format(
        order_number: str,
    ) -> bool:
        """
        التحقق من صحة تنسيق رقم الطلب.
        
        Args:
            order_number: رقم الطلب
            
        Returns:
            bool: True إذا كان التنسيق صحيحاً
        """
        return RestaurantOrderCountersRepository.validate_order_number_format(
            order_number=order_number,
        )

    # ==============================================
    # PARSE ORDER NUMBER
    # ==============================================

    @staticmethod
    def parse_order_number(
        order_number: str,
    ) -> Optional[Dict[str, Any]]:
        """
        تحليل رقم الطلب واستخراج المكونات.
        
        Args:
            order_number: رقم الطلب
            
        Returns:
            Optional[Dict[str, Any]]: مكونات رقم الطلب أو None
        """
        return RestaurantOrderCountersRepository.parse_order_number(
            order_number=order_number,
        )


# ==============================================
# 🔄 COMPATIBILITY FUNCTIONS
# دوال متوافقة مع الاستيرادات القديمة
# ==============================================

# ==============================================
# INITIALIZE ORDER COUNTER (COMPATIBILITY)
# ==============================================

async def initialize_order_counter(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    تهيئة عداد طلبات جديد لمطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على المطعم
        ConflictError: إذا كان العداد موجوداً مسبقاً
    """
    service = RestaurantOrderCounterService(session=session)

    await service.initialize_counter(restaurant_id=restaurant_id)

    logger.info(
        "order_counter_initialized",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# GET ORDER COUNTER (COMPATIBILITY)
# ==============================================

async def get_order_counter(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> Optional[Dict[str, Any]]:
    """
    الحصول على عداد طلبات مطعم معين (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        Optional[Dict[str, Any]]: قاموس بيانات العداد أو None
    """
    service = RestaurantOrderCounterService(session=session)

    try:
        counter = await service.get_counter(restaurant_id=restaurant_id)
        return counter.model_dump()
    except NotFoundError:
        return None


# ==============================================
# INCREMENT ORDER COUNTER (COMPATIBILITY)
# ==============================================

async def increment_order_counter(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    زيادة عداد طلبات مطعم بمقدار 1 (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على العداد
    """
    service = RestaurantOrderCounterService(session=session)

    await service.increment_counter(restaurant_id=restaurant_id)

    logger.info(
        "order_counter_incremented",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# RESET ORDER COUNTER (COMPATIBILITY)
# ==============================================

async def reset_order_counter(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    إعادة تعيين عداد طلبات مطعم إلى الصفر (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على العداد
    """
    service = RestaurantOrderCounterService(session=session)

    await service.reset_counter(restaurant_id=restaurant_id)

    logger.info(
        "order_counter_reset",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# GENERATE ORDER NUMBER (COMPATIBILITY)
# ==============================================

async def generate_order_number(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> str:
    """
    توليد رقم الطلب التالي لمطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        str: رقم الطلب التالي
        
    Raises:
        NotFoundError: إذا لم يتم العثور على العداد
    """
    service = RestaurantOrderCounterService(session=session)

    result = await service.generate_next_order_number(
        restaurant_id=restaurant_id,
    )

    return result.formatted_number


# ==============================================
# GET CURRENT ORDER NUMBER (COMPATIBILITY)
# ==============================================

async def get_current_order_number(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> int:
    """
    الحصول على رقم الطلب الحالي لمطعم معين (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        int: آخر رقم طلب
        
    Raises:
        NotFoundError: إذا لم يتم العثور على العداد
    """
    service = RestaurantOrderCounterService(session=session)

    return await service.get_current_number(restaurant_id=restaurant_id)


# ==============================================
# BUILD ORDER NUMBER (COMPATIBILITY)
# ==============================================

def build_order_number(
    restaurant_id: int,
    sequence: int,
) -> str:
    """
    بناء رقم طلب منسق (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        sequence: رقم التسلسل
        
    Returns:
        str: رقم الطلب المنسق
    """
    return RestaurantOrderCounterService.build_order_number(
        restaurant_id=restaurant_id,
        sequence=sequence,
    )


# ==============================================
# GET ORDER COUNTER SUMMARY (COMPATIBILITY)
# ==============================================

async def get_order_counter_summary(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> CounterSummary:
    """
    الحصول على ملخص عداد طلبات مطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        CounterSummary: ملخص العداد
    """
    service = RestaurantOrderCounterService(session=session)

    summary = await service.get_counter_summary(restaurant_id=restaurant_id)

    return summary.model_dump()
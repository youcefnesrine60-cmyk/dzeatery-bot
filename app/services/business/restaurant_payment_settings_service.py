# ==============================================
# 🏦 RESTAURANT PAYMENT SETTINGS SERVICE
# منطق الأعمال لإعدادات الدفع للمطعم
#
# إنشاء إعدادات الدفع
# قراءة إعدادات الدفع
# تحديث إعدادات الدفع
# حذف إعدادات الدفع
# جلب طرق الدفع المسموح بها
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
from app.models.restaurant_payment_setting import RestaurantPaymentSetting
from app.repositories.restaurant_payment_settings_repo import (
    RestaurantPaymentSettingsRepository,
)

# ✅ استيراد المخططات
from app.schemas.restaurant_payment_setting import (
    RestaurantPaymentSettingCreate,
    RestaurantPaymentSettingResponse,
    RestaurantPaymentSettingUpdate,
    PaymentMethodsList,
    PaymentSettingsSummary,
)


# ==============================================
# 🧩 CONSTANTS
# ==============================================

ALL_PAYMENT_METHODS = ["cash", "card", "ccp", "baridimob", "stripe", "paypal"]
DEFAULT_PAYMENT_METHODS = ["cash", "card"]


# ==============================================
# 🧩 TYPES
# ==============================================

PaymentSettingsData = Dict[str, Any]
PaymentSettingsUpdateData = Dict[str, Any]
SettingsSummary = Dict[str, Any]


# ==============================================
# 🏦 RESTAURANT PAYMENT SETTINGS SERVICE
# ==============================================


class RestaurantPaymentSettingsService:
    """
    خدمة إعدادات الدفع للمطعم - تدير منطق الأعمال لإعدادات الدفع.
    
    مسؤولة عن:
        - إنشاء إعدادات الدفع
        - قراءة إعدادات الدفع
        - تحديث إعدادات الدفع
        - حذف إعدادات الدفع
        - جلب طرق الدفع المسموح بها
    
    Attributes:
        session: جلسة قاعدة البيانات غير المتزامنة
        repo: مستودع إعدادات الدفع
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """
        تهيئة خدمة إعدادات الدفع للمطعم.
        
        Args:
            session: جلسة قاعدة البيانات غير المتزامنة
        """
        self.session = session
        self.repo = RestaurantPaymentSettingsRepository(session)

    # ==========================================
    # 📖 QUERIES
    # ==========================================

    # ==============================================
    # GET SETTINGS
    # ==============================================

    async def get_settings(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantPaymentSettingResponse:
        """
        الحصول على إعدادات الدفع لمطعم معين.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantPaymentSettingResponse: بيانات إعدادات الدفع
            
        Raises:
            NotFoundError: إذا لم يتم العثور على الإعدادات
        """
        logger.info(
            "payment_settings_service_get_settings",
            extra={"restaurant_id": restaurant_id},
        )

        settings = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not settings:
            raise NotFoundError(
                message=f"إعدادات الدفع للمطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        return RestaurantPaymentSettingResponse.model_validate(settings)

    # ==============================================
    # GET ALLOWED METHODS
    # ==============================================

    async def get_allowed_methods(
        self,
        *,
        restaurant_id: int,
    ) -> PaymentMethodsList:
        """
        الحصول على قائمة طرق الدفع المسموح بها لمطعم معين.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            PaymentMethodsList: قائمة طرق الدفع المسموح بها
        """
        logger.info(
            "payment_settings_service_get_allowed_methods",
            extra={"restaurant_id": restaurant_id},
        )

        return await self.repo.get_allowed_methods(
            restaurant_id=restaurant_id,
        )

    # ==============================================
    # IS METHOD ALLOWED
    # ==============================================

    async def is_method_allowed(
        self,
        *,
        restaurant_id: int,
        method: str,
    ) -> bool:
        """
        التحقق من أن طريقة دفع معينة مسموح بها لمطعم.
        
        Args:
            restaurant_id: معرف المطعم
            method: طريقة الدفع (cash, card, ccp, baridimob, stripe, paypal)
            
        Returns:
            bool: True إذا كانت مسموحة، False إذا لم تكن
        """
        # التحقق من صحة طريقة الدفع
        if method.lower() not in ALL_PAYMENT_METHODS:
            raise ValidationError(
                message=f"طريقة الدفع '{method}' غير معروفة",
                details={
                    "method": method,
                    "valid_methods": ALL_PAYMENT_METHODS,
                },
            )

        logger.info(
            "payment_settings_service_is_method_allowed",
            extra={
                "restaurant_id": restaurant_id,
                "method": method,
            },
        )

        allowed_methods = await self.repo.get_allowed_methods(
            restaurant_id=restaurant_id,
        )

        return method.lower() in allowed_methods

    # ==========================================
    # 📊 STATISTICS
    # ==========================================

    # ==============================================
    # GET SETTINGS SUMMARY
    # ==============================================

    async def get_settings_summary(
        self,
        *,
        restaurant_id: int,
    ) -> PaymentSettingsSummary:
        """
        الحصول على ملخص إعدادات الدفع لمطعم.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            PaymentSettingsSummary: ملخص إعدادات الدفع
        """
        logger.info(
            "payment_settings_service_get_summary",
            extra={"restaurant_id": restaurant_id},
        )

        settings = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not settings:
            return PaymentSettingsSummary(
                restaurant_id=restaurant_id,
                exists=False,
                total_enabled=0,
                total_disabled=len(ALL_PAYMENT_METHODS),
                enabled_methods=[],
                disabled_methods=ALL_PAYMENT_METHODS.copy(),
            )

        enabled_methods = []
        disabled_methods = []

        method_map = {
            "cash": settings.allow_cash,
            "card": settings.allow_card,
            "ccp": settings.allow_ccp,
            "baridimob": settings.allow_baridimob,
            "stripe": settings.allow_stripe,
            "paypal": settings.allow_paypal,
        }

        for method, enabled in method_map.items():
            if enabled:
                enabled_methods.append(method)
            else:
                disabled_methods.append(method)

        return PaymentSettingsSummary(
            restaurant_id=restaurant_id,
            exists=True,
            settings_id=settings.id,
            total_enabled=len(enabled_methods),
            total_disabled=len(disabled_methods),
            enabled_methods=enabled_methods,
            disabled_methods=disabled_methods,
        )

    # ==========================================
    # ✏️ MUTATIONS
    # ==========================================

    # ==============================================
    # CREATE SETTINGS
    # ==============================================

    async def create_settings(
        self,
        *,
        settings_data: RestaurantPaymentSettingCreate,
    ) -> RestaurantPaymentSettingResponse:
        """
        إنشاء إعدادات دفع جديدة لمطعم.
        
        Args:
            settings_data: بيانات إعدادات الدفع
            
        Returns:
            RestaurantPaymentSettingResponse: بيانات إعدادات الدفع المنشأة
            
        Raises:
            ConflictError: إذا كانت الإعدادات موجودة مسبقاً
        """
        logger.info(
            "payment_settings_service_create",
            extra={
                "restaurant_id": settings_data.restaurant_id,
                "allow_cash": settings_data.allow_cash,
                "allow_card": settings_data.allow_card,
            },
        )

        # التحقق من عدم وجود إعدادات مسبقة
        existing = await self.repo.get_by_restaurant_id(
            restaurant_id=settings_data.restaurant_id,
        )

        if existing:
            raise ConflictError(
                message=f"إعدادات الدفع للمطعم بـ ID '{settings_data.restaurant_id}' موجودة مسبقاً",
            )

        # إنشاء إعدادات جديدة
        settings = await self.repo.create_settings(
            restaurant_id=settings_data.restaurant_id,
            allow_cash=settings_data.allow_cash,
            allow_card=settings_data.allow_card,
            allow_ccp=settings_data.allow_ccp if settings_data.allow_ccp is not None else False,
            allow_baridimob=settings_data.allow_baridimob if settings_data.allow_baridimob is not None else False,
            allow_stripe=settings_data.allow_stripe if settings_data.allow_stripe is not None else False,
            allow_paypal=settings_data.allow_paypal if settings_data.allow_paypal is not None else False,
        )

        logger.info(
            "payment_settings_created_successfully",
            extra={
                "restaurant_id": settings_data.restaurant_id,
                "settings_id": settings.id,
            },
        )

        return RestaurantPaymentSettingResponse.model_validate(settings)

    # ==============================================
    # UPDATE SETTINGS
    # ==============================================

    async def update_settings(
        self,
        *,
        restaurant_id: int,
        update_data: RestaurantPaymentSettingUpdate,
    ) -> RestaurantPaymentSettingResponse:
        """
        تحديث إعدادات الدفع لمطعم.
        
        Args:
            restaurant_id: معرف المطعم
            update_data: بيانات التحديث
            
        Returns:
            RestaurantPaymentSettingResponse: بيانات إعدادات الدفع المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على الإعدادات
        """
        logger.info(
            "payment_settings_service_update",
            extra={
                "restaurant_id": restaurant_id,
                "fields": list(update_data.model_dump(exclude_unset=True).keys()),
            },
        )

        # التحقق من وجود الإعدادات
        settings = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not settings:
            raise NotFoundError(
                message=f"إعدادات الدفع للمطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        updates = update_data.model_dump(exclude_unset=True)

        # تحديث الإعدادات
        updated = await self.repo.update(
            id=settings.id,
            data=updates,
        )

        if not updated:
            raise NotFoundError(
                message=f"إعدادات الدفع للمطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "payment_settings_updated_successfully",
            extra={"restaurant_id": restaurant_id},
        )

        return RestaurantPaymentSettingResponse.model_validate(updated)

    # ==============================================
    # UPDATE PAYMENT METHODS
    # ==============================================

    async def update_payment_methods(
        self,
        *,
        restaurant_id: int,
        allow_cash: Optional[bool] = None,
        allow_card: Optional[bool] = None,
        allow_ccp: Optional[bool] = None,
        allow_baridimob: Optional[bool] = None,
        allow_stripe: Optional[bool] = None,
        allow_paypal: Optional[bool] = None,
    ) -> RestaurantPaymentSettingResponse:
        """
        تحديث طرق الدفع المسموح بها لمطعم.
        
        Args:
            restaurant_id: معرف المطعم
            allow_cash: السماح بالدفع نقداً (اختياري)
            allow_card: السماح بالدفع ببطاقة POS (اختياري)
            allow_ccp: السماح بالدفع عبر CCP (اختياري)
            allow_baridimob: السماح بالدفع عبر بريدي موب (اختياري)
            allow_stripe: السماح بالدفع عبر Stripe (اختياري)
            allow_paypal: السماح بالدفع عبر PayPal (اختياري)
            
        Returns:
            RestaurantPaymentSettingResponse: بيانات إعدادات الدفع المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على الإعدادات
        """
        logger.info(
            "payment_settings_service_update_methods",
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

        # التحقق من وجود الإعدادات
        settings = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not settings:
            raise NotFoundError(
                message=f"إعدادات الدفع للمطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        # تحديث طرق الدفع
        updated = await self.repo.update_payment_methods(
            restaurant_id=restaurant_id,
            allow_cash=allow_cash,
            allow_card=allow_card,
            allow_ccp=allow_ccp,
            allow_baridimob=allow_baridimob,
            allow_stripe=allow_stripe,
            allow_paypal=allow_paypal,
        )

        if not updated:
            raise NotFoundError(
                message=f"إعدادات الدفع للمطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "payment_methods_updated_successfully",
            extra={"restaurant_id": restaurant_id},
        )

        return RestaurantPaymentSettingResponse.model_validate(updated)

    # ==============================================
    # ENABLE PAYMENT METHOD
    # ==============================================

    async def enable_payment_method(
        self,
        *,
        restaurant_id: int,
        method: str,
    ) -> RestaurantPaymentSettingResponse:
        """
        تفعيل طريقة دفع معينة لمطعم.
        
        Args:
            restaurant_id: معرف المطعم
            method: طريقة الدفع المراد تفعيلها
            
        Returns:
            RestaurantPaymentSettingResponse: بيانات إعدادات الدفع المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على الإعدادات
            ValidationError: إذا كانت طريقة الدفع غير معروفة
        """
        if method.lower() not in ALL_PAYMENT_METHODS:
            raise ValidationError(
                message=f"طريقة الدفع '{method}' غير معروفة",
                details={
                    "method": method,
                    "valid_methods": ALL_PAYMENT_METHODS,
                },
            )

        logger.info(
            "payment_settings_service_enable_method",
            extra={
                "restaurant_id": restaurant_id,
                "method": method,
            },
        )

        # بناء بيانات التحديث
        updates = {method.lower(): True}

        return await self.update_payment_methods(
            restaurant_id=restaurant_id,
            **updates,
        )

    # ==============================================
    # DISABLE PAYMENT METHOD
    # ==============================================

    async def disable_payment_method(
        self,
        *,
        restaurant_id: int,
        method: str,
    ) -> RestaurantPaymentSettingResponse:
        """
        إلغاء تفعيل طريقة دفع معينة لمطعم.
        
        Args:
            restaurant_id: معرف المطعم
            method: طريقة الدفع المراد إلغاء تفعيلها
            
        Returns:
            RestaurantPaymentSettingResponse: بيانات إعدادات الدفع المحدثة
            
        Raises:
            NotFoundError: إذا لم يتم العثور على الإعدادات
            ValidationError: إذا كانت طريقة الدفع غير معروفة
        """
        if method.lower() not in ALL_PAYMENT_METHODS:
            raise ValidationError(
                message=f"طريقة الدفع '{method}' غير معروفة",
                details={
                    "method": method,
                    "valid_methods": ALL_PAYMENT_METHODS,
                },
            )

        logger.info(
            "payment_settings_service_disable_method",
            extra={
                "restaurant_id": restaurant_id,
                "method": method,
            },
        )

        # بناء بيانات التحديث
        updates = {method.lower(): False}

        return await self.update_payment_methods(
            restaurant_id=restaurant_id,
            **updates,
        )

    # ==============================================
    # DELETE SETTINGS
    # ==============================================

    async def delete_settings(
        self,
        *,
        restaurant_id: int,
    ) -> None:
        """
        حذف إعدادات الدفع لمطعم.
        
        Args:
            restaurant_id: معرف المطعم
            
        Raises:
            NotFoundError: إذا لم يتم العثور على الإعدادات
        """
        logger.info(
            "payment_settings_service_delete",
            extra={"restaurant_id": restaurant_id},
        )

        # التحقق من وجود الإعدادات
        settings = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not settings:
            raise NotFoundError(
                message=f"إعدادات الدفع للمطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        # حذف الإعدادات
        deleted = await self.repo.delete(id=settings.id)

        if not deleted:
            raise NotFoundError(
                message=f"إعدادات الدفع للمطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "payment_settings_deleted_successfully",
            extra={"restaurant_id": restaurant_id},
        )

    # ==============================================
    # RESET TO DEFAULTS
    # ==============================================

    async def reset_to_defaults(
        self,
        *,
        restaurant_id: int,
    ) -> RestaurantPaymentSettingResponse:
        """
        إعادة تعيين إعدادات الدفع إلى القيم الافتراضية.
        
        Args:
            restaurant_id: معرف المطعم
            
        Returns:
            RestaurantPaymentSettingResponse: بيانات إعدادات الدفع المعاد تعيينها
            
        Raises:
            NotFoundError: إذا لم يتم العثور على الإعدادات
        """
        logger.info(
            "payment_settings_service_reset",
            extra={"restaurant_id": restaurant_id},
        )

        # التحقق من وجود الإعدادات
        settings = await self.repo.get_by_restaurant_id(
            restaurant_id=restaurant_id,
        )

        if not settings:
            raise NotFoundError(
                message=f"إعدادات الدفع للمطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        # إعادة تعيين الإعدادات إلى القيم الافتراضية
        updated = await self.repo.update_payment_methods(
            restaurant_id=restaurant_id,
            allow_cash=True,
            allow_card=True,
            allow_ccp=False,
            allow_baridimob=False,
            allow_stripe=False,
            allow_paypal=False,
        )

        if not updated:
            raise NotFoundError(
                message=f"إعدادات الدفع للمطعم بـ ID '{restaurant_id}' غير موجودة",
            )

        logger.info(
            "payment_settings_reset_successfully",
            extra={"restaurant_id": restaurant_id},
        )

        return RestaurantPaymentSettingResponse.model_validate(updated)


# ==============================================
# 🔄 COMPATIBILITY FUNCTIONS
# دوال متوافقة مع الاستيرادات القديمة
# ==============================================

# ==============================================
# CREATE PAYMENT SETTINGS (COMPATIBILITY)
# ==============================================

async def create_payment_settings(
    *,
    restaurant_id: int,
    allow_cash: bool = True,
    allow_card: bool = True,
    allow_ccp: bool = False,
    allow_baridimob: bool = False,
    allow_stripe: bool = False,
    allow_paypal: bool = False,
    session: AsyncSession,
) -> int:
    """
    إنشاء إعدادات دفع جديدة لمطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        allow_cash: السماح بالدفع نقداً
        allow_card: السماح بالدفع ببطاقة POS
        allow_ccp: السماح بالدفع عبر CCP
        allow_baridimob: السماح بالدفع عبر بريدي موب
        allow_stripe: السماح بالدفع عبر Stripe
        allow_paypal: السماح بالدفع عبر PayPal
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        int: معرف إعدادات الدفع
        
    Raises:
        ConflictError: إذا كانت الإعدادات موجودة مسبقاً
    """
    service = RestaurantPaymentSettingsService(session=session)

    settings_data = RestaurantPaymentSettingCreate(
        restaurant_id=restaurant_id,
        allow_cash=allow_cash,
        allow_card=allow_card,
        allow_ccp=allow_ccp,
        allow_baridimob=allow_baridimob,
        allow_stripe=allow_stripe,
        allow_paypal=allow_paypal,
    )

    settings = await service.create_settings(
        settings_data=settings_data,
    )

    return settings.id


# ==============================================
# GET PAYMENT SETTINGS (COMPATIBILITY)
# ==============================================

async def get_payment_settings(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> Optional[Dict[str, Any]]:
    """
    الحصول على إعدادات الدفع لمطعم معين (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        Optional[Dict[str, Any]]: قاموس بيانات إعدادات الدفع أو None
    """
    service = RestaurantPaymentSettingsService(session=session)

    try:
        settings = await service.get_settings(restaurant_id=restaurant_id)
        return settings.model_dump()
    except NotFoundError:
        return None


# ==============================================
# UPDATE PAYMENT SETTINGS (COMPATIBILITY)
# ==============================================

async def update_payment_settings(
    *,
    restaurant_id: int,
    data: PaymentSettingsUpdateData,
    session: AsyncSession,
) -> None:
    """
    تحديث إعدادات الدفع لمطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        data: بيانات التحديث
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على الإعدادات
    """
    service = RestaurantPaymentSettingsService(session=session)

    update_data = RestaurantPaymentSettingUpdate(**data)

    await service.update_settings(
        restaurant_id=restaurant_id,
        update_data=update_data,
    )

    logger.info(
        "payment_settings_updated",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# UPDATE PAYMENT METHODS (COMPATIBILITY)
# ==============================================

async def update_payment_methods(
    *,
    restaurant_id: int,
    allow_cash: Optional[bool] = None,
    allow_card: Optional[bool] = None,
    allow_ccp: Optional[bool] = None,
    allow_baridimob: Optional[bool] = None,
    allow_stripe: Optional[bool] = None,
    allow_paypal: Optional[bool] = None,
    session: AsyncSession,
) -> None:
    """
    تحديث طرق الدفع المسموح بها لمطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        allow_cash: السماح بالدفع نقداً (اختياري)
        allow_card: السماح بالدفع ببطاقة POS (اختياري)
        allow_ccp: السماح بالدفع عبر CCP (اختياري)
        allow_baridimob: السماح بالدفع عبر بريدي موب (اختياري)
        allow_stripe: السماح بالدفع عبر Stripe (اختياري)
        allow_paypal: السماح بالدفع عبر PayPal (اختياري)
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على الإعدادات
    """
    service = RestaurantPaymentSettingsService(session=session)

    await service.update_payment_methods(
        restaurant_id=restaurant_id,
        allow_cash=allow_cash,
        allow_card=allow_card,
        allow_ccp=allow_ccp,
        allow_baridimob=allow_baridimob,
        allow_stripe=allow_stripe,
        allow_paypal=allow_paypal,
    )

    logger.info(
        "payment_methods_updated",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# GET ALLOWED PAYMENT METHODS (COMPATIBILITY)
# ==============================================

async def get_allowed_payment_methods(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> PaymentMethodsList:
    """
    الحصول على قائمة طرق الدفع المسموح بها لمطعم معين (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Returns:
        PaymentMethodsList: قائمة طرق الدفع المسموح بها
    """
    service = RestaurantPaymentSettingsService(session=session)

    return await service.get_allowed_methods(restaurant_id=restaurant_id)


# ==============================================
# DELETE PAYMENT SETTINGS (COMPATIBILITY)
# ==============================================

async def delete_payment_settings(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    حذف إعدادات الدفع لمطعم (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على الإعدادات
    """
    service = RestaurantPaymentSettingsService(session=session)

    await service.delete_settings(restaurant_id=restaurant_id)

    logger.info(
        "payment_settings_deleted",
        extra={"restaurant_id": restaurant_id},
    )


# ==============================================
# RESET PAYMENT SETTINGS (COMPATIBILITY)
# ==============================================

async def reset_payment_settings(
    *,
    restaurant_id: int,
    session: AsyncSession,
) -> None:
    """
    إعادة تعيين إعدادات الدفع إلى القيم الافتراضية (دالة متوافقة مع الإصدار القديم).
    
    Args:
        restaurant_id: معرف المطعم
        session: جلسة قاعدة البيانات غير المتزامنة
        
    Raises:
        NotFoundError: إذا لم يتم العثور على الإعدادات
    """
    service = RestaurantPaymentSettingsService(session=session)

    await service.reset_to_defaults(restaurant_id=restaurant_id)

    logger.info(
        "payment_settings_reset",
        extra={"restaurant_id": restaurant_id},
    )
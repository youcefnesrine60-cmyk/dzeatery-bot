# ==============================================
# 🏦 RESTAURANT PAYMENT SETTING SCHEMAS
# نماذج Pydantic لإعدادات الدفع للمطعم
# تدير التحقق من صحة البيانات وتسلسلها لإعدادات الدفع
# ==============================================

from datetime import datetime
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
)


# ==============================================
# 🧩 TYPES
# ==============================================

PaymentSettingData = Dict[str, Any]
PaymentSettingUpdateData = Dict[str, Any]
PaymentSettingListData = List[Dict[str, Any]]
AllowedMethodsList = List[str]


# ==============================================
# 📦 BASE SCHEMA
# ==============================================

class RestaurantPaymentSettingBase(BaseModel):
    """
    المخطط الأساسي لإعدادات الدفع للمطعم.
    
    يحتوي على الحقول المشتركة بين جميع مخططات إعدادات الدفع.
    
    Attributes:
        restaurant_id: معرف المطعم
        allow_cash: السماح بالدفع نقداً
        allow_card: السماح بالدفع ببطاقة POS
        allow_ccp: السماح بالدفع عبر CCP
        allow_baridimob: السماح بالدفع عبر بريدي موب
        allow_stripe: السماح بالدفع عبر Stripe
        allow_paypal: السماح بالدفع عبر PayPal
    """
    restaurant_id: int = Field(
        ...,
        description="معرف المطعم",
        example=1,
        ge=1,
    )
    allow_cash: bool = Field(
        True,
        description="السماح بالدفع نقداً",
        example=True,
    )
    allow_card: bool = Field(
        True,
        description="السماح بالدفع ببطاقة POS",
        example=True,
    )
    allow_ccp: bool = Field(
        False,
        description="السماح بالدفع عبر CCP",
        example=False,
    )
    allow_baridimob: bool = Field(
        False,
        description="السماح بالدفع عبر بريدي موب",
        example=False,
    )
    allow_stripe: bool = Field(
        False,
        description="السماح بالدفع عبر Stripe",
        example=False,
    )
    allow_paypal: bool = Field(
        False,
        description="السماح بالدفع عبر PayPal",
        example=False,
    )


# ==============================================
# 📥 CREATE SCHEMA
# ==============================================

class RestaurantPaymentSettingCreate(BaseModel):
    """
    مخطط إنشاء إعدادات الدفع للمطعم.
    
    Attributes:
        restaurant_id: معرف المطعم
        allow_cash: السماح بالدفع نقداً (اختياري)
        allow_card: السماح بالدفع ببطاقة POS (اختياري)
        allow_ccp: السماح بالدفع عبر CCP (اختياري)
        allow_baridimob: السماح بالدفع عبر بريدي موب (اختياري)
        allow_stripe: السماح بالدفع عبر Stripe (اختياري)
        allow_paypal: السماح بالدفع عبر PayPal (اختياري)
    """
    restaurant_id: int = Field(
        ...,
        description="معرف المطعم",
        example=1,
        ge=1,
    )
    allow_cash: bool = Field(
        True,
        description="السماح بالدفع نقداً",
        example=True,
    )
    allow_card: bool = Field(
        True,
        description="السماح بالدفع ببطاقة POS",
        example=True,
    )
    allow_ccp: bool = Field(
        False,
        description="السماح بالدفع عبر CCP",
        example=False,
    )
    allow_baridimob: bool = Field(
        False,
        description="السماح بالدفع عبر بريدي موب",
        example=False,
    )
    allow_stripe: bool = Field(
        False,
        description="السماح بالدفع عبر Stripe",
        example=False,
    )
    allow_paypal: bool = Field(
        False,
        description="السماح بالدفع عبر PayPal",
        example=False,
    )


# ==============================================
# 📤 UPDATE SCHEMA
# ==============================================

class RestaurantPaymentSettingUpdate(BaseModel):
    """
    مخطط تحديث إعدادات الدفع - جميع الحقول اختيارية.
    
    Attributes:
        allow_cash: السماح بالدفع نقداً
        allow_card: السماح بالدفع ببطاقة POS
        allow_ccp: السماح بالدفع عبر CCP
        allow_baridimob: السماح بالدفع عبر بريدي موب
        allow_stripe: السماح بالدفع عبر Stripe
        allow_paypal: السماح بالدفع عبر PayPal
    """
    allow_cash: Optional[bool] = Field(
        None,
        description="السماح بالدفع نقداً",
        example=True,
    )
    allow_card: Optional[bool] = Field(
        None,
        description="السماح بالدفع ببطاقة POS",
        example=True,
    )
    allow_ccp: Optional[bool] = Field(
        None,
        description="السماح بالدفع عبر CCP",
        example=False,
    )
    allow_baridimob: Optional[bool] = Field(
        None,
        description="السماح بالدفع عبر بريدي موب",
        example=False,
    )
    allow_stripe: Optional[bool] = Field(
        None,
        description="السماح بالدفع عبر Stripe",
        example=False,
    )
    allow_paypal: Optional[bool] = Field(
        None,
        description="السماح بالدفع عبر PayPal",
        example=False,
    )


# ==============================================
# 📤 RESPONSE SCHEMA
# ==============================================

class RestaurantPaymentSettingResponse(RestaurantPaymentSettingBase):
    """
    مخطط استجابة إعدادات الدفع - يحتوي على جميع الحقول بما فيها التواريخ.
    
    Attributes:
        id: معرف الإعداد
        created_at: تاريخ الإنشاء
        updated_at: تاريخ آخر تحديث
    """
    id: int = Field(
        ...,
        description="معرف الإعداد",
        example=1,
        ge=1,
    )
    created_at: datetime = Field(
        ...,
        description="تاريخ الإنشاء",
    )
    updated_at: datetime = Field(
        ...,
        description="تاريخ آخر تحديث",
    )

    class Config:
        """
        إعدادات نموذج Pydantic.
        """
        from_attributes = True


# ==============================================
# 📋 LIST RESPONSE
# ==============================================

class RestaurantPaymentSettingListResponse(BaseModel):
    """
    مخطط استجابة قائمة إعدادات الدفع للمطعم.
    
    يحتوي على قائمة إعدادات الدفع مع معلومات الترقيم.
    
    Attributes:
        items: قائمة إعدادات الدفع
        total: العدد الإجمالي
        skip: عدد السجلات المتخطية
        limit: الحد الأقصى للسجلات
    """
    items: List[RestaurantPaymentSettingResponse] = Field(
        ...,
        description="قائمة إعدادات الدفع",
    )
    total: int = Field(
        ...,
        description="العدد الإجمالي",
        example=10,
        ge=0,
    )
    skip: int = Field(
        ...,
        description="عدد السجلات المتخطية",
        example=0,
        ge=0,
    )
    limit: int = Field(
        ...,
        description="الحد الأقصى للسجلات",
        example=100,
        ge=1,
    )


# ==============================================
# 📋 PAYMENT METHODS LIST
# ==============================================

class PaymentMethodsList(BaseModel):
    """
    مخطط قائمة طرق الدفع المسموح بها.
    
    Attributes:
        restaurant_id: معرف المطعم
        allowed_methods: قائمة طرق الدفع المسموح بها
        all_methods: قائمة جميع طرق الدفع المتاحة
    """
    restaurant_id: int = Field(
        ...,
        description="معرف المطعم",
        example=1,
    )
    allowed_methods: AllowedMethodsList = Field(
        ...,
        description="قائمة طرق الدفع المسموح بها",
        example=["cash", "card"],
    )
    all_methods: AllowedMethodsList = Field(
        ...,
        description="قائمة جميع طرق الدفع المتاحة",
        example=["cash", "card", "ccp", "baridimob", "stripe", "paypal"],
    )


# ==============================================
# 📊 PAYMENT SETTINGS SUMMARY
# ==============================================

class PaymentSettingsSummary(BaseModel):
    """
    مخطط ملخص إعدادات الدفع.
    
    Attributes:
        restaurant_id: معرف المطعم
        total_enabled: عدد طرق الدفع المفعّلة
        total_disabled: عدد طرق الدفع المعطّلة
        enabled_methods: قائمة طرق الدفع المفعّلة
        disabled_methods: قائمة طرق الدفع المعطّلة
    """
    restaurant_id: int = Field(
        ...,
        description="معرف المطعم",
        example=1,
    )
    total_enabled: int = Field(
        ...,
        description="عدد طرق الدفع المفعّلة",
        example=2,
        ge=0,
    )
    total_disabled: int = Field(
        ...,
        description="عدد طرق الدفع المعطّلة",
        example=4,
        ge=0,
    )
    enabled_methods: AllowedMethodsList = Field(
        ...,
        description="قائمة طرق الدفع المفعّلة",
        example=["cash", "card"],
    )
    disabled_methods: AllowedMethodsList = Field(
        ...,
        description="قائمة طرق الدفع المعطّلة",
        example=["ccp", "baridimob", "stripe", "paypal"],
    )


# ==============================================
# 📋 EXPORTS
# ==============================================

__all__ = [
    "RestaurantPaymentSettingBase",
    "RestaurantPaymentSettingCreate",
    "RestaurantPaymentSettingUpdate",
    "RestaurantPaymentSettingResponse",
    "RestaurantPaymentSettingListResponse",
    "PaymentMethodsList",
    "PaymentSettingsSummary",
    "PaymentSettingData",
    "PaymentSettingUpdateData",
    "PaymentSettingListData",
]
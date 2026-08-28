# ==============================================
# 🍽️ RESTAURANT SCHEMAS
# نماذج Pydantic للمطاعم
# تدير التحقق من صحة البيانات وتسلسلها للمطاعم
# ==============================================

from datetime import datetime
from typing import (
    Dict,
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


# ==============================================
# 🧩 TYPES
# ==============================================

RestaurantData = Dict[str, any]
RestaurantUpdateData = Dict[str, any]
RestaurantListData = List[Dict[str, any]]


# ==============================================
# 📦 BASE SCHEMA
# ==============================================

class RestaurantBase(BaseModel):
    """
    المخطط الأساسي للمطعم.
    
    يحتوي على الحقول المشتركة بين جميع مخططات المطعم.
    
    Attributes:
        owner_id: معرف المالك
        group_id: معرف المجموعة
        name: اسم المطعم
        type: نوع المطعم
        phone: رقم الهاتف
        wilaya: الولاية
        lat: خط العرض
        lng: خط الطول
        is_active: حالة النشاط
    """
    owner_id: int = Field(
        ...,
        description="معرف المالك",
        example=1,
        ge=1,
    )
    group_id: Optional[int] = Field(
        None,
        description="معرف المجموعة",
        example=1,
    )
    name: str = Field(
        ...,
        max_length=255,
        description="اسم المطعم",
        example="مطعم البيتزا السريعة",
        min_length=2,
    )
    type: str = Field(
        ...,
        max_length=100,
        description="نوع المطعم",
        example="بيتزا",
        min_length=2,
    )
    phone: str = Field(
        ...,
        max_length=20,
        description="رقم الهاتف",
        example="0555123456",
    )
    wilaya: str = Field(
        ...,
        max_length=100,
        description="الولاية",
        example="Alger",
        min_length=2,
    )
    lat: Optional[float] = Field(
        None,
        description="خط العرض",
        example=36.7538,
    )
    lng: Optional[float] = Field(
        None,
        description="خط الطول",
        example=3.0588,
    )
    is_active: bool = Field(
        True,
        description="حالة النشاط",
        example=True,
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """
        التحقق من صحة رقم الهاتف.
        
        Args:
            value: رقم الهاتف
            
        Returns:
            رقم الهاتف المدقق
            
        Raises:
            ValueError: إذا كان رقم الهاتف غير صالح
        """
        cleaned = value.replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise ValueError("رقم الهاتف يجب أن يحتوي على أرقام فقط")
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("رقم الهاتف يجب أن يكون بين 10 و 15 رقماً")
        return cleaned

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        """
        التحقق من صحة نوع المطعم.
        
        Args:
            value: نوع المطعم
            
        Returns:
            نوع المطعم المدقق
            
        Raises:
            ValueError: إذا كان النوع غير صالح
        """
        valid_types = {"restaurant", "cafe", "fast_food", "bakery", "pizza", "other"}
        if value.lower() not in valid_types:
            raise ValueError(f"نوع المطعم يجب أن يكون واحداً من: {', '.join(valid_types)}")
        return value.lower()


# ==============================================
# 📥 CREATE SCHEMA
# ==============================================

class RestaurantCreate(RestaurantBase):
    """
    مخطط إنشاء مطعم جديد.
    
    يرث جميع حقول RestaurantBase مع إمكانية إضافة حقول إضافية.
    """
    pass


# ==============================================
# 📤 UPDATE SCHEMA
# ==============================================

class RestaurantUpdate(BaseModel):
    """
    مخطط تحديث مطعم - جميع الحقول اختيارية.
    
    Attributes:
        owner_id: معرف المالك
        group_id: معرف المجموعة
        name: اسم المطعم
        type: نوع المطعم
        phone: رقم الهاتف
        wilaya: الولاية
        lat: خط العرض
        lng: خط الطول
        is_active: حالة النشاط
    """
    owner_id: Optional[int] = Field(
        None,
        description="معرف المالك",
        ge=1,
    )
    group_id: Optional[int] = Field(
        None,
        description="معرف المجموعة",
    )
    name: Optional[str] = Field(
        None,
        max_length=255,
        description="اسم المطعم",
        min_length=2,
    )
    type: Optional[str] = Field(
        None,
        max_length=100,
        description="نوع المطعم",
        min_length=2,
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="رقم الهاتف",
    )
    wilaya: Optional[str] = Field(
        None,
        max_length=100,
        description="الولاية",
        min_length=2,
    )
    lat: Optional[float] = Field(
        None,
        description="خط العرض",
    )
    lng: Optional[float] = Field(
        None,
        description="خط الطول",
    )
    is_active: Optional[bool] = Field(
        None,
        description="حالة النشاط",
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """
        التحقق من صحة رقم الهاتف.
        
        Args:
            value: رقم الهاتف
            
        Returns:
            رقم الهاتف المدقق
            
        Raises:
            ValueError: إذا كان رقم الهاتف غير صالح
        """
        if value is not None:
            cleaned = value.replace(" ", "").replace("-", "")
            if not cleaned.isdigit():
                raise ValueError("رقم الهاتف يجب أن يحتوي على أرقام فقط")
            if len(cleaned) < 10 or len(cleaned) > 15:
                raise ValueError("رقم الهاتف يجب أن يكون بين 10 و 15 رقماً")
            return cleaned
        return value

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: Optional[str]) -> Optional[str]:
        """
        التحقق من صحة نوع المطعم.
        
        Args:
            value: نوع المطعم
            
        Returns:
            نوع المطعم المدقق
            
        Raises:
            ValueError: إذا كان النوع غير صالح
        """
        if value is not None:
            valid_types = {"restaurant", "cafe", "fast_food", "bakery", "pizza", "other"}
            if value.lower() not in valid_types:
                raise ValueError(f"نوع المطعم يجب أن يكون واحداً من: {', '.join(valid_types)}")
            return value.lower()
        return value


# ==============================================
# 📤 RESPONSE SCHEMA
# ==============================================

class RestaurantResponse(RestaurantBase):
    """
    مخطط استجابة المطعم.
    
    يحتوي على جميع حقول المطعم مع الحقول الإضافية للاستجابة.
    
    Attributes:
        id: معرف المطعم
        created_at: تاريخ الإنشاء
        updated_at: تاريخ آخر تحديث
    """
    id: int = Field(
        ...,
        description="معرف المطعم",
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

class RestaurantListResponse(BaseModel):
    """
    مخطط استجابة قائمة المطاعم.
    
    يحتوي على قائمة المطاعم مع معلومات الترقيم.
    
    Attributes:
        items: قائمة المطاعم
        total: العدد الإجمالي
        skip: عدد السجلات المتخطية
        limit: الحد الأقصى للسجلات
    """
    items: List[RestaurantResponse] = Field(
        ...,
        description="قائمة المطاعم",
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
# 📊 STATS SCHEMA
# ==============================================

class RestaurantStats(BaseModel):
    """
    مخطط إحصائيات المطعم.
    
    يحتوي على إحصائيات ومعلومات موجزة عن المطعم.
    
    Attributes:
        total_restaurants: إجمالي عدد المطاعم
        active_restaurants: عدد المطاعم النشطة
        inactive_restaurants: عدد المطاعم غير النشطة
        type_distribution: توزيع المطاعم حسب النوع
        wilaya_distribution: توزيع المطاعم حسب الولاية
    """
    total_restaurants: int = Field(
        ...,
        description="إجمالي عدد المطاعم",
        example=10,
        ge=0,
    )
    active_restaurants: int = Field(
        ...,
        description="عدد المطاعم النشطة",
        example=8,
        ge=0,
    )
    inactive_restaurants: int = Field(
        ...,
        description="عدد المطاعم غير النشطة",
        example=2,
        ge=0,
    )
    type_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="توزيع المطاعم حسب النوع",
        example={"pizza": 3, "fast_food": 2, "restaurant": 5},
    )
    wilaya_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="توزيع المطاعم حسب الولاية",
        example={"Alger": 4, "Oran": 3, "Constantine": 3},
    )


# ==============================================
# 📋 EXPORTS
# ==============================================

__all__ = [
    "RestaurantBase",
    "RestaurantCreate",
    "RestaurantUpdate",
    "RestaurantResponse",
    "RestaurantListResponse",
    "RestaurantStats",
    "RestaurantData",
    "RestaurantUpdateData",
    "RestaurantListData",
]
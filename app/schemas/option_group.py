# ==============================================
# 🎛 OPTION GROUP SCHEMAS
# نماذج Pydantic لمجموعات الخيارات
# تدير التحقق من صحة البيانات وتسلسلها لمجموعات الخيارات
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

OptionGroupData = Dict[str, Any]
OptionGroupUpdateData = Dict[str, Any]
OptionGroupListData = List[Dict[str, Any]]


# ==============================================
# 📦 BASE SCHEMA
# ==============================================

class OptionGroupBase(BaseModel):
    """
    المخطط الأساسي لمجموعة الخيارات.
    
    Attributes:
        product_id: معرف المنتج
        name: اسم مجموعة الخيارات
        required: هل المجموعة إجبارية
        multiple_choice: هل يسمح باختيار متعدد
        sort_order: ترتيب العرض
    """
    product_id: int = Field(
        ...,
        description="معرف المنتج",
        example=1,
    )
    name: str = Field(
        ...,
        max_length=255,
        description="اسم مجموعة الخيارات",
        example="حجم البيتزا",
    )
    required: bool = Field(
        False,
        description="هل المجموعة إجبارية",
        example=True,
    )
    multiple_choice: bool = Field(
        False,
        description="هل يسمح باختيار متعدد",
        example=False,
    )
    sort_order: int = Field(
        0,
        description="ترتيب العرض",
        example=1,
    )


# ==============================================
# 📥 CREATE SCHEMA
# ==============================================

class OptionGroupCreate(BaseModel):
    """
    مخطط إنشاء مجموعة خيارات جديدة.
    
    Attributes:
        product_id: معرف المنتج
        name: اسم مجموعة الخيارات
        required: هل المجموعة إجبارية
        multiple_choice: هل يسمح باختيار متعدد
        sort_order: ترتيب العرض
    """
    product_id: int = Field(
        ...,
        description="معرف المنتج",
        example=1,
    )
    name: str = Field(
        ...,
        max_length=255,
        description="اسم مجموعة الخيارات",
        example="حجم البيتزا",
    )
    required: bool = Field(
        False,
        description="هل المجموعة إجبارية",
        example=True,
    )
    multiple_choice: bool = Field(
        False,
        description="هل يسمح باختيار متعدد",
        example=False,
    )
    sort_order: int = Field(
        0,
        description="ترتيب العرض",
        example=1,
    )


# ==============================================
# 📤 UPDATE SCHEMA
# ==============================================

class OptionGroupUpdate(BaseModel):
    """
    مخطط تحديث مجموعة خيارات.
    
    Attributes:
        name: اسم مجموعة الخيارات الجديد
        required: هل المجموعة إجبارية
        multiple_choice: هل يسمح باختيار متعدد
        sort_order: ترتيب العرض الجديد
    """
    name: Optional[str] = Field(
        None,
        max_length=255,
        description="اسم مجموعة الخيارات الجديد",
        example="حجم البيتزا",
    )
    required: Optional[bool] = Field(
        None,
        description="هل المجموعة إجبارية",
        example=False,
    )
    multiple_choice: Optional[bool] = Field(
        None,
        description="هل يسمح باختيار متعدد",
        example=True,
    )
    sort_order: Optional[int] = Field(
        None,
        description="ترتيب العرض الجديد",
        example=2,
    )


# ==============================================
# 📤 RESPONSE SCHEMA
# ==============================================

class OptionGroupResponse(OptionGroupBase):
    """
    مخطط استجابة مجموعة الخيارات.
    
    Attributes:
        id: معرف مجموعة الخيارات
        created_at: تاريخ الإنشاء
        updated_at: تاريخ آخر تحديث
    """
    id: int = Field(
        ...,
        description="معرف مجموعة الخيارات",
        example=1,
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
# 🎯 OPTION GROUP WITH OPTIONS
# ==============================================

class ProductOptionResponse(BaseModel):
    """
    مخطط استجابة خيار المنتج.
    
    Attributes:
        id: معرف الخيار
        name: اسم الخيار
        extra_price: السعر الإضافي
        is_available: حالة التوفر
        sort_order: ترتيب العرض
    """
    id: int = Field(
        ...,
        description="معرف الخيار",
        example=1,
    )
    name: str = Field(
        ...,
        description="اسم الخيار",
        example="كبير",
    )
    extra_price: float = Field(
        ...,
        description="السعر الإضافي",
        example=200.00,
    )
    is_available: bool = Field(
        ...,
        description="حالة التوفر",
        example=True,
    )
    sort_order: int = Field(
        ...,
        description="ترتيب العرض",
        example=1,
    )


class OptionGroupWithOptionsResponse(OptionGroupResponse):
    """
    مخطط استجابة مجموعة الخيارات مع خياراتها.
    
    Attributes:
        options: قائمة خيارات المنتج
    """
    options: List[ProductOptionResponse] = Field(
        default_factory=list,
        description="خيارات المنتج",
    )


# ==============================================
# 📋 LIST RESPONSE
# ==============================================

class OptionGroupListResponse(BaseModel):
    """
    مخطط استجابة قائمة مجموعات الخيارات.
    
    Attributes:
        items: قائمة مجموعات الخيارات
        total: العدد الإجمالي
        skip: عدد السجلات المتخطية
        limit: الحد الأقصى للسجلات
    """
    items: List[OptionGroupResponse] = Field(
        ...,
        description="قائمة مجموعات الخيارات",
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
# 📊 SUMMARY
# ==============================================

class OptionGroupSummary(BaseModel):
    """
    مخطط ملخص مجموعات الخيارات.
    
    Attributes:
        product_id: معرف المنتج
        total_groups: إجمالي عدد المجموعات
        required_groups: عدد المجموعات الإجبارية
        optional_groups: عدد المجموعات الاختيارية
        total_options: إجمالي عدد الخيارات
    """
    product_id: int = Field(
        ...,
        description="معرف المنتج",
        example=1,
    )
    total_groups: int = Field(
        ...,
        description="إجمالي عدد المجموعات",
        example=5,
        ge=0,
    )
    required_groups: int = Field(
        ...,
        description="عدد المجموعات الإجبارية",
        example=3,
        ge=0,
    )
    optional_groups: int = Field(
        ...,
        description="عدد المجموعات الاختيارية",
        example=2,
        ge=0,
    )
    total_options: int = Field(
        ...,
        description="إجمالي عدد الخيارات",
        example=15,
        ge=0,
    )


# ==============================================
# ✅ VALIDATION
# ==============================================

class OptionGroupValidation(BaseModel):
    """
    مخطط التحقق من صحة مجموعة الخيارات.
    
    Attributes:
        product_id: معرف المنتج
        name: اسم مجموعة الخيارات
        required: هل المجموعة إجبارية
        multiple_choice: هل يسمح باختيار متعدد
    """
    product_id: int = Field(
        ...,
        description="معرف المنتج",
        example=1,
    )
    name: str = Field(
        ...,
        max_length=255,
        description="اسم مجموعة الخيارات",
        example="حجم البيتزا",
    )
    required: bool = Field(
        False,
        description="هل المجموعة إجبارية",
        example=True,
    )
    multiple_choice: bool = Field(
        False,
        description="هل يسمح باختيار متعدد",
        example=False,
    )


# ==============================================
# 📋 EXPORTS
# ==============================================

__all__ = [
    "OptionGroupBase",
    "OptionGroupCreate",
    "OptionGroupUpdate",
    "OptionGroupResponse",
    "ProductOptionResponse",
    "OptionGroupWithOptionsResponse",
    "OptionGroupListResponse",
    "OptionGroupSummary",
    "OptionGroupValidation",
    "OptionGroupData",
    "OptionGroupUpdateData",
    "OptionGroupListData",
]
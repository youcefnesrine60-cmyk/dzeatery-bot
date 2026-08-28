# ==============================================
# 📂 CATEGORY SCHEMAS
# نماذج Pydantic للتصنيفات
# تدير التحقق من صحة البيانات وتسلسلها للتصنيفات
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

CategoryData = Dict[str, Any]
CategoryUpdateData = Dict[str, Any]


# ==============================================
# 📦 BASE SCHEMA
# ==============================================

class CategoryBase(BaseModel):
    """
    المخطط الأساسي للتصنيف.
    
    يحتوي على الحقول المشتركة بين جميع مخططات التصنيف.
    
    Attributes:
        restaurant_id: معرف المطعم
        name: اسم التصنيف
        sort_order: ترتيب العرض
    """
    restaurant_id: int = Field(
        ...,
        description="معرف المطعم",
        example=1,
    )
    name: str = Field(
        ...,
        max_length=255,
        description="اسم التصنيف",
        example="بيتزا",
    )
    sort_order: int = Field(
        0,
        description="ترتيب العرض",
        example=1,
    )


# ==============================================
# 📥 CREATE SCHEMA
# ==============================================

class CategoryCreate(BaseModel):
    """
    مخطط إنشاء تصنيف جديد.
    
    Attributes:
        name: اسم التصنيف
        sort_order: ترتيب العرض (اختياري)
    """
    name: str = Field(
        ...,
        max_length=255,
        description="اسم التصنيف",
        example="بيتزا",
    )
    sort_order: int = Field(
        0,
        description="ترتيب العرض",
        example=1,
    )


# ==============================================
# 📤 UPDATE SCHEMA
# ==============================================

class CategoryUpdate(BaseModel):
    """
    مخطط تحديث التصنيف - جميع الحقول اختيارية.
    
    Attributes:
        name: اسم التصنيف
        sort_order: ترتيب العرض
    """
    name: Optional[str] = Field(
        None,
        max_length=255,
        description="اسم التصنيف",
        example="بيتزا",
    )
    sort_order: Optional[int] = Field(
        None,
        description="ترتيب العرض",
        example=1,
    )


# ==============================================
# 📤 RESPONSE SCHEMA
# ==============================================

class CategoryResponse(CategoryBase):
    """
    مخطط استجابة التصنيف - يحتوي على جميع الحقول بما فيها التواريخ.
    
    Attributes:
        id: معرف التصنيف
        created_at: تاريخ الإنشاء
        updated_at: تاريخ آخر تحديث
    """
    id: int = Field(
        ...,
        description="معرف التصنيف",
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
# 📋 CATEGORY LIST RESPONSE
# ==============================================

class CategoryListResponse(BaseModel):
    """
    مخطط استجابة قائمة التصنيفات.
    
    يحتوي على قائمة التصنيفات مع معلومات الترقيم.
    
    Attributes:
        items: قائمة التصنيفات
        total: العدد الإجمالي
        skip: عدد السجلات المتخطية
        limit: الحد الأقصى للسجلات
    """
    items: List[CategoryResponse] = Field(
        ...,
        description="قائمة التصنيفات",
    )
    total: int = Field(
        ...,
        description="العدد الإجمالي",
        example=10,
    )
    skip: int = Field(
        ...,
        description="عدد السجلات المتخطية",
        example=0,
    )
    limit: int = Field(
        ...,
        description="الحد الأقصى للسجلات",
        example=100,
    )


# ==============================================
# 📊 CATEGORY SUMMARY
# ==============================================

class CategorySummary(BaseModel):
    """
    مخطط ملخص التصنيفات.
    
    يحتوي على إحصائيات موجزة عن التصنيفات.
    
    Attributes:
        total_categories: إجمالي عدد التصنيفات
        categories_with_products: عدد التصنيفات التي تحتوي على منتجات
        empty_categories: عدد التصنيفات الفارغة
        total_products: إجمالي عدد المنتجات في جميع التصنيفات
        avg_products_per_category: متوسط عدد المنتجات لكل تصنيف
    """
    total_categories: int = Field(
        ...,
        description="إجمالي عدد التصنيفات",
        example=10,
    )
    categories_with_products: int = Field(
        ...,
        description="عدد التصنيفات التي تحتوي على منتجات",
        example=8,
    )
    empty_categories: int = Field(
        ...,
        description="عدد التصنيفات الفارغة",
        example=2,
    )
    total_products: int = Field(
        ...,
        description="إجمالي عدد المنتجات في جميع التصنيفات",
        example=50,
    )
    avg_products_per_category: float = Field(
        ...,
        description="متوسط عدد المنتجات لكل تصنيف",
        example=5.0,
    )
# ==============================================
# 👤 USER SCHEMAS
# نماذج Pydantic للمستخدمين
# تدير التحقق من صحة البيانات وتسلسلها للمستخدمين
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

UserData = Dict[str, Any]
UserUpdateData = Dict[str, Any]
UserList = List["UserResponse"]

# ==============================================
# 📦 BASE SCHEMA
# ==============================================

class UserBase(BaseModel):
    """
    المخطط الأساسي للمستخدم.
    
    يحتوي على الحقول المشتركة بين جميع مخططات المستخدم.
    
    Attributes:
        chat_id: معرف المستخدم في تيليجرام
        consent: موافقة المستخدم على الشروط والأحكام
        customer_name: اسم العميل
        customer_phone: رقم هاتف العميل
    """
    chat_id: Optional[int] = Field(
        None,
        description="معرف المستخدم في تيليجرام",
        example=123456789,
    )
    consent: bool = Field(
        False,
        description="موافقة المستخدم على الشروط والأحكام",
        example=True,
    )
    customer_name: Optional[str] = Field(
        None,
        max_length=255,
        description="اسم العميل",
        example="أحمد محمد",
    )
    customer_phone: Optional[str] = Field(
        None,
        max_length=20,
        description="رقم هاتف العميل",
        example="0555123456",
    )


# ==============================================
# 📥 CREATE SCHEMA
# ==============================================

class UserCreate(BaseModel):
    """
    مخطط إنشاء مستخدم جديد.
    
    Attributes:
        chat_id: معرف المستخدم في تيليجرام
        consent: موافقة المستخدم (اختياري)
        customer_name: اسم العميل (اختياري)
        customer_phone: رقم هاتف العميل (اختياري)
    """
    chat_id: int = Field(
        ...,
        description="معرف المستخدم في تيليجرام",
        example=123456789,
    )
    consent: bool = Field(
        False,
        description="موافقة المستخدم على الشروط والأحكام",
        example=True,
    )
    customer_name: Optional[str] = Field(
        None,
        max_length=255,
        description="اسم العميل",
        example="أحمد محمد",
    )
    customer_phone: Optional[str] = Field(
        None,
        max_length=20,
        description="رقم هاتف العميل",
        example="0555123456",
    )


# ==============================================
# 📤 UPDATE SCHEMA
# ==============================================

class UserUpdate(BaseModel):
    """
    مخطط تحديث المستخدم - جميع الحقول اختيارية.
    
    Attributes:
        consent: موافقة المستخدم
        customer_name: اسم العميل
        customer_phone: رقم هاتف العميل
    """
    consent: Optional[bool] = Field(
        None,
        description="موافقة المستخدم على الشروط والأحكام",
        example=True,
    )
    customer_name: Optional[str] = Field(
        None,
        max_length=255,
        description="اسم العميل",
        example="أحمد محمد",
    )
    customer_phone: Optional[str] = Field(
        None,
        max_length=20,
        description="رقم هاتف العميل",
        example="0555123456",
    )


# ==============================================
# ✅ CONSENT UPDATE SCHEMA
# ==============================================

class UserConsentUpdate(BaseModel):
    """
    مخطط تحديث موافقة المستخدم.
    
    Attributes:
        consent: حالة الموافقة الجديدة
    """
    consent: bool = Field(
        ...,
        description="حالة الموافقة الجديدة",
        example=True,
    )


# ==============================================
# 📤 RESPONSE SCHEMA
# ==============================================

class UserResponse(UserBase):
    """
    مخطط استجابة المستخدم - يحتوي على جميع الحقول بما فيها التواريخ.
    
    Attributes:
        id: معرف المستخدم
        created_at: تاريخ الإنشاء
        updated_at: تاريخ آخر تحديث
    """
    id: int = Field(
        ...,
        description="معرف المستخدم",
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
# 📋 USER LIST RESPONSE
# ==============================================

class UserListResponse(BaseModel):
    """
    مخطط استجابة قائمة المستخدمين.
    
    Attributes:
        items: قائمة المستخدمين
        total: العدد الإجمالي
        skip: عدد السجلات المتخطية
        limit: الحد الأقصى للسجلات
    """
    items: UserList = Field(
        ...,
        description="قائمة المستخدمين",
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
# 📊 USER SUMMARY
# ==============================================

class UserSummary(BaseModel):
    """
    مخطط ملخص المستخدمين.
    
    Attributes:
        total_users: إجمالي عدد المستخدمين
        users_with_consent: عدد المستخدمين بالموافقة
        users_without_consent: عدد المستخدمين بدون موافقة
        users_with_name: عدد المستخدمين بالاسم
        users_with_phone: عدد المستخدمين برقم الهاتف
        consent_rate: نسبة الموافقة
        profile_completion_rate: نسبة اكتمال الملف الشخصي
    """
    total_users: int = Field(
        ...,
        description="إجمالي عدد المستخدمين",
        example=100,
    )
    users_with_consent: int = Field(
        ...,
        description="عدد المستخدمين بالموافقة",
        example=80,
    )
    users_without_consent: int = Field(
        ...,
        description="عدد المستخدمين بدون موافقة",
        example=20,
    )
    users_with_name: int = Field(
        ...,
        description="عدد المستخدمين بالاسم",
        example=70,
    )
    users_with_phone: int = Field(
        ...,
        description="عدد المستخدمين برقم الهاتف",
        example=60,
    )
    consent_rate: float = Field(
        ...,
        description="نسبة الموافقة (%)",
        example=80.0,
    )
    profile_completion_rate: float = Field(
        ...,
        description="نسبة اكتمال الملف الشخصي (%)",
        example=65.0,
    )


# ==============================================
# 🔍 USER SEARCH
# ==============================================

class UserSearch(BaseModel):
    """
    مخطط البحث عن المستخدمين.
    
    Attributes:
        query: نص البحث
        skip: عدد السجلات المتخطية
        limit: الحد الأقصى للسجلات
    """
    query: str = Field(
        ...,
        min_length=1,
        description="نص البحث (الاسم أو رقم الهاتف)",
        example="أحمد",
    )
    skip: int = Field(
        0,
        ge=0,
        description="عدد السجلات المتخطية",
        example=0,
    )
    limit: int = Field(
        100,
        ge=1,
        le=100,
        description="الحد الأقصى للسجلات",
        example=10,
    )


# ==============================================
# ✅ CONSENT RESPONSE
# ==============================================

class ConsentResponse(BaseModel):
    """
    مخطط استجابة الموافقة.
    
    Attributes:
        chat_id: معرف المستخدم
        has_consent: حالة الموافقة
        message: رسالة توضيحية
    """
    chat_id: int = Field(
        ...,
        description="معرف المستخدم في تيليجرام",
        example=123456789,
    )
    has_consent: bool = Field(
        ...,
        description="حالة الموافقة",
        example=True,
    )
    message: str = Field(
        ...,
        description="رسالة توضيحية",
        example="User has given consent",
    )
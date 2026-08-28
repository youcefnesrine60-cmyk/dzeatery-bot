# ==============================================
# 👤 OWNER SCHEMAS
# نماذج Pydantic للمالكين
# تدير التحقق من صحة البيانات وتسلسلها للمالكين
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
    field_validator,
)


# ==============================================
# 🧩 TYPES
# ==============================================

OwnerData = Dict[str, Any]
OwnerUpdateData = Dict[str, Any]
OwnerListData = List[Dict[str, Any]]


# ==============================================
# 📦 BASE SCHEMA
# ==============================================

class OwnerBase(BaseModel):
    """
    المخطط الأساسي للمالك.
    
    يحتوي على الحقول المشتركة بين جميع مخططات المالك.
    
    Attributes:
        chat_id: معرف المستخدم في تيليجرام
        full_name: الاسم الكامل
        phone: رقم الهاتف
        email: البريد الإلكتروني
    """
    chat_id: int = Field(
        ...,
        description="معرف المستخدم في تيليجرام",
        example=123456789,
        ge=1,
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="الاسم الكامل",
        example="أحمد محمد",
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="رقم الهاتف",
        example="0555123456",
    )
    email: Optional[str] = Field(
        None,
        max_length=255,
        description="البريد الإلكتروني",
        example="ahmed@example.com",
    )

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        """
        التحقق من صحة البريد الإلكتروني.
        
        Args:
            value: البريد الإلكتروني
            
        Returns:
            البريد الإلكتروني المدقق
            
        Raises:
            ValueError: إذا كان البريد الإلكتروني غير صالح
        """
        if value is not None:
            if "@" not in value:
                raise ValueError("البريد الإلكتروني غير صالح")
            if "." not in value.split("@")[-1]:
                raise ValueError("البريد الإلكتروني غير صالح")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
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
            # إزالة المسافات والشرطات
            cleaned = value.replace(" ", "").replace("-", "")
            
            # التحقق من أن الرقم يتكون من أرقام فقط
            if not cleaned.isdigit():
                raise ValueError("رقم الهاتف يجب أن يحتوي على أرقام فقط")
            
            # التحقق من الطول (للأرقام الجزائرية)
            if len(cleaned) < 10 or len(cleaned) > 15:
                raise ValueError("رقم الهاتف يجب أن يكون بين 10 و 15 رقماً")
            
            return cleaned
        return value


# ==============================================
# 📥 CREATE SCHEMA
# ==============================================

class OwnerCreate(OwnerBase):
    """
    مخطط إنشاء مالك جديد.
    
    يرث جميع حقول OwnerBase مع إضافة حقل الحالة.
    
    Attributes:
        registration_status: حالة التسجيل (اختياري)
        trial_used: هل استخدم الفترة التجريبية (اختياري)
    """
    registration_status: Optional[str] = Field(
        "pending",
        max_length=50,
        description="حالة التسجيل",
        example="pending",
    )
    trial_used: Optional[bool] = Field(
        False,
        description="هل استخدم الفترة التجريبية",
        example=False,
    )

    @field_validator("registration_status")
    @classmethod
    def validate_registration_status(
        cls,
        value: str,
    ) -> str:
        """
        التحقق من صحة حالة التسجيل.
        
        Args:
            value: حالة التسجيل
            
        Returns:
            حالة التسجيل المدققة
            
        Raises:
            ValueError: إذا كانت الحالة غير صالحة
        """
        valid_statuses = {"pending", "approved", "rejected"}
        if value not in valid_statuses:
            raise ValueError(f"حالة التسجيل يجب أن تكون واحدة من: {', '.join(valid_statuses)}")
        return value


# ==============================================
# 📤 UPDATE SCHEMA
# ==============================================

class OwnerUpdate(BaseModel):
    """
    مخطط تحديث المالك.
    
    جميع الحقول اختيارية لتحديث جزئي.
    
    Attributes:
        full_name: الاسم الكامل
        phone: رقم الهاتف
        email: البريد الإلكتروني
        registration_status: حالة التسجيل
        trial_used: هل استخدم الفترة التجريبية
    """
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="الاسم الكامل",
        example="أحمد محمد علي",
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="رقم الهاتف",
        example="0555123456",
    )
    email: Optional[str] = Field(
        None,
        max_length=255,
        description="البريد الإلكتروني",
        example="ahmed.ali@example.com",
    )
    registration_status: Optional[str] = Field(
        None,
        max_length=50,
        description="حالة التسجيل",
        example="approved",
    )
    trial_used: Optional[bool] = Field(
        None,
        description="هل استخدم الفترة التجريبية",
        example=True,
    )

    @field_validator("email")
    @classmethod
    def validate_email(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        """
        التحقق من صحة البريد الإلكتروني.
        
        Args:
            value: البريد الإلكتروني
            
        Returns:
            البريد الإلكتروني المدقق
            
        Raises:
            ValueError: إذا كان البريد الإلكتروني غير صالح
        """
        if value is not None:
            if "@" not in value:
                raise ValueError("البريد الإلكتروني غير صالح")
            if "." not in value.split("@")[-1]:
                raise ValueError("البريد الإلكتروني غير صالح")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
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

    @field_validator("registration_status")
    @classmethod
    def validate_registration_status(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        """
        التحقق من صحة حالة التسجيل.
        
        Args:
            value: حالة التسجيل
            
        Returns:
            حالة التسجيل المدققة
            
        Raises:
            ValueError: إذا كانت الحالة غير صالحة
        """
        if value is not None:
            valid_statuses = {"pending", "approved", "rejected"}
            if value not in valid_statuses:
                raise ValueError(f"حالة التسجيل يجب أن تكون واحدة من: {', '.join(valid_statuses)}")
        return value


# ==============================================
# 📤 STATUS UPDATE SCHEMA
# ==============================================

class OwnerStatusUpdate(BaseModel):
    """
    مخطط تحديث حالة المالك.
    
    يستخدم لتحديث حالة التسجيل فقط.
    
    Attributes:
        registration_status: حالة التسجيل الجديدة
    """
    registration_status: str = Field(
        ...,
        max_length=50,
        description="حالة التسجيل الجديدة",
        example="approved",
    )

    @field_validator("registration_status")
    @classmethod
    def validate_registration_status(
        cls,
        value: str,
    ) -> str:
        """
        التحقق من صحة حالة التسجيل.
        
        Args:
            value: حالة التسجيل
            
        Returns:
            حالة التسجيل المدققة
            
        Raises:
            ValueError: إذا كانت الحالة غير صالحة
        """
        valid_statuses = {"pending", "approved", "rejected"}
        if value not in valid_statuses:
            raise ValueError(f"حالة التسجيل يجب أن تكون واحدة من: {', '.join(valid_statuses)}")
        return value


# ==============================================
# 📤 RESPONSE SCHEMA
# ==============================================

class OwnerResponse(OwnerBase):
    """
    مخطط استجابة المالك.
    
    يحتوي على جميع حقول المالك مع الحقول الإضافية للاستجابة.
    
    Attributes:
        id: معرف المالك
        registration_status: حالة التسجيل
        trial_used: هل استخدم الفترة التجريبية
        created_at: تاريخ الإنشاء
        updated_at: تاريخ آخر تحديث
    """
    id: int = Field(
        ...,
        description="معرف المالك",
        example=1,
        ge=1,
    )
    registration_status: str = Field(
        ...,
        description="حالة التسجيل",
        example="approved",
    )
    trial_used: bool = Field(
        ...,
        description="هل استخدم الفترة التجريبية",
        example=False,
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

class OwnerListResponse(BaseModel):
    """
    مخطط استجابة قائمة المالكين.
    
    يحتوي على قائمة المالكين مع معلومات الترقيم.
    
    Attributes:
        items: قائمة المالكين
        total: العدد الإجمالي
        skip: عدد السجلات المتخطية
        limit: الحد الأقصى للسجلات
    """
    items: List[OwnerResponse] = Field(
        ...,
        description="قائمة المالكين",
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
# 📊 OWNER STATISTICS
# ==============================================

class OwnerStatistics(BaseModel):
    """
    مخطط إحصائيات المالكين.
    
    يحتوي على إحصائيات موجزة عن المالكين.
    
    Attributes:
        total: إجمالي عدد المالكين
        pending: عدد المالكين المعلقين
        approved: عدد المالكين المعتمدين
        rejected: عدد المالكين المرفوضين
        trial_used: عدد المالكين الذين استخدموا الفترة التجريبية
        trial_available: عدد المالكين الذين لم يستخدموا الفترة التجريبية
    """
    total: int = Field(
        ...,
        description="إجمالي عدد المالكين",
        example=100,
        ge=0,
    )
    pending: int = Field(
        ...,
        description="عدد المالكين المعلقين",
        example=10,
        ge=0,
    )
    approved: int = Field(
        ...,
        description="عدد المالكين المعتمدين",
        example=80,
        ge=0,
    )
    rejected: int = Field(
        ...,
        description="عدد المالكين المرفوضين",
        example=10,
        ge=0,
    )
    trial_used: int = Field(
        ...,
        description="عدد المالكين الذين استخدموا الفترة التجريبية",
        example=30,
        ge=0,
    )
    trial_available: int = Field(
        ...,
        description="عدد المالكين الذين لم يستخدموا الفترة التجريبية",
        example=50,
        ge=0,
    )


# ==============================================
# 🔍 SEARCH
# ==============================================

class OwnerSearch(BaseModel):
    """
    مخطط البحث عن المالكين.
    
    Attributes:
        query: نص البحث
        status: تصفية حسب حالة التسجيل
        skip: عدد السجلات المتخطية
        limit: الحد الأقصى للسجلات
    """
    query: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="نص البحث",
        example="أحمد",
    )
    status: Optional[str] = Field(
        None,
        max_length=50,
        description="تصفية حسب حالة التسجيل",
        example="approved",
    )
    skip: int = Field(
        0,
        description="عدد السجلات المتخطية",
        example=0,
        ge=0,
    )
    limit: int = Field(
        100,
        description="الحد الأقصى للسجلات",
        example=100,
        ge=1,
        le=1000,
    )

    @field_validator("status")
    @classmethod
    def validate_status(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        """
        التحقق من صحة حالة التسجيل.
        
        Args:
            value: حالة التسجيل
            
        Returns:
            حالة التسجيل المدققة
            
        Raises:
            ValueError: إذا كانت الحالة غير صالحة
        """
        if value is not None:
            valid_statuses = {"pending", "approved", "rejected"}
            if value not in valid_statuses:
                raise ValueError(f"حالة التسجيل يجب أن تكون واحدة من: {', '.join(valid_statuses)}")
        return value


# ==============================================
# 🎁 TRIAL
# ==============================================

class TrialActivation(BaseModel):
    """
    مخطط تفعيل الفترة التجريبية.
    
    Attributes:
        owner_id: معرف المالك
    """
    owner_id: int = Field(
        ...,
        description="معرف المالك",
        example=1,
        ge=1,
    )


class TrialActivationResponse(BaseModel):
    """
    مخطط استجابة تفعيل الفترة التجريبية.
    
    Attributes:
        owner_id: معرف المالك
        trial_used: حالة استخدام الفترة التجريبية
        activated_at: تاريخ التفعيل
        message: رسالة تأكيد
    """
    owner_id: int = Field(
        ...,
        description="معرف المالك",
        example=1,
    )
    trial_used: bool = Field(
        ...,
        description="حالة استخدام الفترة التجريبية",
        example=True,
    )
    activated_at: datetime = Field(
        ...,
        description="تاريخ التفعيل",
    )
    message: str = Field(
        ...,
        description="رسالة تأكيد",
        example="تم تفعيل الفترة التجريبية بنجاح",
    )


# ==============================================
# 📋 EXPORTS
# ==============================================

__all__ = [
    "OwnerBase",
    "OwnerCreate",
    "OwnerUpdate",
    "OwnerStatusUpdate",
    "OwnerResponse",
    "OwnerListResponse",
    "OwnerStatistics",
    "OwnerSearch",
    "TrialActivation",
    "TrialActivationResponse",
    "OwnerData",
    "OwnerUpdateData",
    "OwnerListData",
]
# ==============================================
# 📦 ORDERS SERVICE - CONSTANTS
# الثوابت (LOCKED_STATUSES, ORDERS_FEATURE_ID)
# ==============================================

from typing import Set

# ==============================================
# 🧩 FEATURE ID
# ==============================================

# معرف ميزة الطلبات في نظام الميزات
ORDERS_FEATURE_ID: int = 6

# ==============================================
# 🔒 LOCKED STATUSES
# ==============================================

# الحالات التي تمنع تعديل الطلب (Lock Order)
# عندما يكون الطلب في هذه الحالات، لا يمكن تعديله أو إلغاؤه
LOCKED_STATUSES: Set[str] = {
    "delivering",   # قيد التوصيل
    "delivered",    # تم التوصيل
    "completed",    # مكتمل
    "cancelled",    # ملغى
}

# ==============================================
# 🟢 ALLOWED TRANSITIONS
# ==============================================

# الانتقالات المسموحة بين الحالات
# المفتاح: الحالة الحالية، القيمة: قائمة الحالات المسموح الانتقال إليها
ALLOWED_TRANSITIONS: dict[str, Set[str]] = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"preparing", "cancelled"},
    "preparing": {"ready", "cancelled"},
    "ready": {"delivering", "cancelled"},
    "delivering": {"delivered", "cancelled"},
    "delivered": {"completed"},
    "completed": set(),
    "cancelled": set(),
}

# ==============================================
# 📊 STATUS_DISPLAY_NAMES
# ==============================================

# الأسماء المعروضة لكل حالة (للواجهات)
STATUS_DISPLAY_NAMES: dict[str, str] = {
    "pending": "⏳ قيد الانتظار",
    "confirmed": "✅ مؤكد",
    "preparing": "👨‍🍳 قيد التحضير",
    "ready": "🍽️ جاهز",
    "delivering": "🚚 قيد التوصيل",
    "delivered": "📦 تم التوصيل",
    "completed": "✅ مكتمل",
    "cancelled": "❌ ملغى",
}

# ==============================================
# 🎨 STATUS_COLORS
# ==============================================

# الألوان لكل حالة (للواجهات)
STATUS_COLORS: dict[str, str] = {
    "pending": "#FFA500",      # برتقالي
    "confirmed": "#2196F3",    # أزرق
    "preparing": "#FF9800",    # برتقالي غامق
    "ready": "#4CAF50",        # أخضر
    "delivering": "#9C27B0",   # بنفسجي
    "delivered": "#00BCD4",    # فيروزي
    "completed": "#8BC34A",    # أخضر فاتح
    "cancelled": "#F44336",    # أحمر
}

# ==============================================
# 🔄 STATUS_ORDER
# ==============================================

# ترتيب الحالات (للعرض في التقارير)
STATUS_ORDER: dict[str, int] = {
    "pending": 1,
    "confirmed": 2,
    "preparing": 3,
    "ready": 4,
    "delivering": 5,
    "delivered": 6,
    "completed": 7,
    "cancelled": 8,
}

# ==============================================
# 📋 STATUS_DESCRIPTIONS
# ==============================================

# وصف لكل حالة
STATUS_DESCRIPTIONS: dict[str, str] = {
    "pending": "تم استلام الطلب في انتظار التأكيد",
    "confirmed": "تم تأكيد الطلب من قبل المطعم",
    "preparing": "الطلب قيد التحضير في المطبخ",
    "ready": "الطلب جاهز للتسليم أو التوصيل",
    "delivering": "الطلب في طريقه إلى العميل",
    "delivered": "تم توصيل الطلب إلى العميل",
    "completed": "اكتمل الطلب بنجاح",
    "cancelled": "تم إلغاء الطلب",
}

# ==============================================
# 🧩 TYPE ALIASES
# ==============================================

StatusType = str
StatusSet = Set[str]
StatusDict = dict[str, str]
StatusTransitionDict = dict[str, Set[str]]
StatusOrderDict = dict[str, int]
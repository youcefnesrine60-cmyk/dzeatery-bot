# ==============================================
# 📦 ORDERS SERVICE - CONSTANTS
# الثوابت (LOCKED_STATUSES, ORDERS_FEATURE_ID)
# ==============================================

# معرف ميزة الطلبات في نظام الميزات
ORDERS_FEATURE_ID = 6

# الحالات التي تمنع تعديل الطلب (Lock Order)
LOCKED_STATUSES = {
    "delivering",
    "delivered",
    "completed",
    "cancelled",
}
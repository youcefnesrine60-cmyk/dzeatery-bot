# ==============================================
# 🎨 UI BUILDERS
# ==============================================

from app.core.logger import (
    logger
)

# ==============================================
# 🏠 MAIN MENU
# ==============================================

def main_menu_ui() -> dict:

    logger.info("display_main_menu")

    return {
        "inline_keyboard": [

            [{
                "text": "🍽️ زبون مطعم",
                "callback_data": "customer"
            }],

            [{
                "text": "🏪 صاحب محل",
                "callback_data": "owner"
            }]
        ]
    }

# ==============================================
# ✅ CONSENT UI
# ==============================================

def consent_ui(

    role: str

) -> dict:

    logger.info(

        "display_consent_ui",

        extra={
            "role": role
        }
    )

    return {
        "inline_keyboard": [

            [{
                "text": "✅ أوافق",
                "callback_data": f"consent_{role}"
            }],

            [{
                "text": "❌ لا أوافق",
                "callback_data": "decline"
            }]
        ]
    }

# ==============================================
# 📜 CONSENT TEXT
# ==============================================

def consent_text() -> str:

    logger.info("display_consent_text")

    return (

        "📢 <b>إشعار قانوني/خاص بالدولة الجزائرية</b>\n\n"

        "<b><u>سياسة حماية المعطيات ذات الطابع الشخصي</u></b>\n\n"

        "باستخدامك هذا البوت، فإنك توافق على معالجة بياناتك ذات الطابع الشخصي "
        "طبقاً لأحكام القانون رقم 18-07 المؤرخ في 10 يونيو 2018 "
        "المتعلق بحماية الأشخاص الطبيعيين في مجال معالجة المعطيات ذات الطابع الشخصي، "
        "المعدل والمتمم بالقانون 25-11 المؤرخ في 24 يوليو 2025.\n\n"

        "🔐 حقوقك:\n"
        "• الحق في الاطلاع على بياناتك\n"
        "• الحق في تصحيحها\n"
        "• الحق في حذفها\n"
        "• الحق في سحب الموافقة في أي وقت\n\n"

        "⚠️ بالضغط على (أوافق) فإنك تقبل هذه الشروط."
    )

# ==============================================
# 🔙 BACK UI
# ==============================================

def back_ui() -> dict:

    logger.info("display_back_ui")

    return {
        "inline_keyboard": [

            [{
                "text": "🔙 رجوع",
                "callback_data": "back_step"
            }]
        ]
    }

# ==============================================
# 📍 LOCATION WEBAPP UI
# ==============================================

def location_webapp_ui() -> dict:

    logger.info("display_location_webapp_ui")

    return {
        "inline_keyboard": [

            [{
                "text": "📍 تحديد موقع المحل",

                "web_app": {
                    "url": "https://dzeatery.onrender.com/map"
                }
            }],

            [{
                "text": "🔙 رجوع",
                "callback_data": "back_step"
            }]
        ]
    }

# ==============================================
# 🍽️ RESTAURANTS UI
# ==============================================

def restaurants_ui(

    restaurants: list

) -> dict:

    logger.info(

        "display_restaurants_ui",

        extra={
            "count": len(restaurants)
        }
    )

    buttons = []

    for restaurant in restaurants:

        buttons.append([{

            "text": f"🍔 {restaurant['name']}",

            "callback_data": f"rest_{restaurant['id']}"
        }])

    buttons.append([{

        "text": "🔙 رجوع",

        "callback_data": "back_main"
    }])

    return {

        "inline_keyboard": buttons
    }

# ==============================================
# 🍔 RESTAURANT ACTIONS UI
# ==============================================

def restaurant_actions_ui(

    restaurant_id: int

) -> dict:

    logger.info(

        "display_restaurant_actions_ui",

        extra={
            "restaurant_id": restaurant_id
        }
    )

    return {
        "inline_keyboard": [

            [{
                "text": "📦 طلب",
                "callback_data": f"order_{restaurant_id}"
            }],

            [{
                "text": "🔙 رجوع",
                "callback_data": "show_restaurants"
            }]
        ]
    }

# ==============================================
# 🍽️ RESTAURANT TYPES UI
# ==============================================

def types_ui() -> dict:

    logger.info("display_types_ui")

    return {
        "inline_keyboard": [

            [{
                "text": "1- مطعم تقليدي",
                "callback_data": "type_traditional"
            }],

            [{
                "text": "2- Fast Food",
                "callback_data": "type_fastfood"
            }],

            [{
                "text": "3- مشاوي",
                "callback_data": "type_grill"
            }],

            [{
                "text": "4- مطعم فاخر",
                "callback_data": "type_luxury"
            }],

            [{
                "text": "5- أكل شعبي",
                "callback_data": "type_popular"
            }],

            [{
                "text": "6- مقهى 24 ساعة",
                "callback_data": "type_cafe"
            }],

            [{
                "text": "7- حلويات",
                "callback_data": "type_sweets"
            }],

            [{
                "text": "🔙 رجوع",
                "callback_data": "back_main"
            }]
        ]
    }

# ==============================================
# ✅ CONFIRM UI
# ==============================================

def confirm_ui() -> dict:

    logger.info("display_confirm_ui")

    return {
        "inline_keyboard": [

            [{
                "text": "✅ تأكيد التسجيل",
                "callback_data": "confirm"
            }],

            [{
                "text": "🔙 رجوع",
                "callback_data": "back_main"
            }]
        ]
    }
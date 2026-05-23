# ==============================================
# 🎨 UI BUILDERS
# ==============================================

from app.core.logger import (
    logger
)

# ==============================================
# 🔘 BUTTON HELPER
# ==============================================

def button(

    text: str,

    callback: str

) -> dict:

    return {

        "text": text,
        "callback_data": callback
    }


# ==============================================
# 🏠 MAIN MENU
# ==============================================

def main_menu_ui() -> dict:

    logger.info(
        "display_main_menu"
    )

    return {

        "inline_keyboard": [

            [
                button(
                    "🍽️ زبون مطعم",
                    "customer"
                )
            ],

            [
                button(
                    "🏪 صاحب محل",
                    "owner"
                )
            ]

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

    keyboard = {

        "inline_keyboard": [

            [
                button(
                    "✅ أوافق",
                    f"consent_{role}"
                )
            ],

            [
                button(
                    "❌ لا أوافق",
                    "decline"
                )
            ]

        ]
    }

    logger.info(

        "consent_ui_generated",

        extra={
            "keyboard": keyboard
        }
    )

    return keyboard


# ==============================================
# 📜 CONSENT TEXT
# ==============================================

def consent_text() -> str:

    logger.info(
        "display_consent_text"
    )

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

    logger.info(
        "display_back_ui"
    )

    return {

        "inline_keyboard": [

            [
                button(
                    "🔙 رجوع",
                    "back_step"
                )
            ]

        ]
    }


# ==============================================
# 📍 LOCATION WEBAPP UI
# ==============================================

def location_webapp_ui() -> dict:

    logger.info(
        "display_location_webapp_ui"
    )

    return {

        "inline_keyboard": [

            [
                {
                    "text": "📍 تحديد موقع المحل",

                    "web_app": {
                        "url": "https://dzeatery.onrender.com/map"
                    }
                }
            ],

            [
                button(
                    "🔙 رجوع",
                    "back_step"
                )
            ]

        ]
    }


# ==============================================
# 🍽️ RESTAURANTS UI
# ==============================================

def restaurants_ui(

    restaurants: list[dict]

) -> dict:

    logger.info(

        "display_restaurants_ui",

        extra={
            "count": len(restaurants)
        }
    )

    # ==========================================
    # 🚫 EMPTY LIST
    # ==========================================

    if not restaurants:

        logger.warning(
            "no_restaurants_found"
        )

        return {

            "inline_keyboard": [

                [
                    button(
                        "❌ لا توجد مطاعم",
                        "noop"
                    )
                ],

                [
                    button(
                        "🔙 رجوع",
                        "back_main"
                    )
                ]

            ]
        }

    # ==========================================
    # 🍔 RESTAURANTS
    # ==========================================

    buttons = []

    for restaurant in restaurants:

        restaurant_name = restaurant.get(
            "name",
            "Unknown"
        )

        restaurant_id = restaurant.get(
            "id",
            0
        )

        buttons.append(

            [

                button(
                    f"🍔 {restaurant_name}",
                    f"rest_{restaurant_id}"
                )

            ]
        )

    # ==========================================
    # 🔙 BACK BUTTON
    # ==========================================

    buttons.append(

        [

            button(
                "🔙 رجوع",
                "back_main"
            )

        ]
    )

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

            [
                button(
                    "📦 طلب",
                    f"order_{restaurant_id}"
                )
            ],

            [
                button(
                    "🔙 رجوع",
                    "show_restaurants"
                )
            ]

        ]
    }


# ==============================================
# 🍽️ RESTAURANT TYPES UI
# ==============================================

def types_ui() -> dict:

    logger.info(
        "display_types_ui"
    )

    return {

        "inline_keyboard": [

            [
                button(
                    "1- مطعم تقليدي",
                    "type_traditional"
                )
            ],

            [
                button(
                    "2- Fast Food",
                    "type_fastfood"
                )
            ],

            [
                button(
                    "3- مشاوي",
                    "type_grill"
                )
            ],

            [
                button(
                    "4- مطعم فاخر",
                    "type_luxury"
                )
            ],

            [
                button(
                    "5- أكل شعبي",
                    "type_popular"
                )
            ],

            [
                button(
                    "6- مقهى 24 ساعة",
                    "type_cafe"
                )
            ],

            [
                button(
                    "7- حلويات",
                    "type_sweets"
                )
            ],

            [
                button(
                    "🔙 رجوع",
                    "back_main"
                )
            ]

        ]
    }


# ==============================================
# ✅ CONFIRM UI
# ==============================================

def confirm_ui() -> dict:

    logger.info(
        "display_confirm_ui"
    )

    return {

        "inline_keyboard": [

            [
                button(
                    "✅ تأكيد التسجيل",
                    "confirm"
                )
            ],

            [
                button(
                    "🔙 رجوع",
                    "back_main"
                )
            ]

        ]
    }
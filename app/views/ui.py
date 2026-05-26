# ==============================================
# 🎨 UI BUILDERS
# ==============================================

from app.core.logger import (
    logger
)

# ==============================================
# 🌐 CONSTANTS
# ==============================================

MAP_URL = "https://dzeatery.onrender.com/map"

# ==============================================
# 🔘 BUTTON HELPER
# ==============================================

def button(

    *,

    text: str,

    callback: str

) -> dict:

    logger.debug(

        "creating_button",

        extra={
            "callback": callback
        }
    )

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

                    text = "🍽️ زبون مطعم",

                    callback = "customer"
                )
            ],

            [
                button(

                    text = "🏪 صاحب محل",

                    callback = "owner"
                )
            ]

        ]
    }

# ==============================================
# ✅ CONSENT UI
# ==============================================

def consent_ui(

    *,

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

            [
                button(

                    text = "✅ أوافق",

                    callback = f"consent_{role}"
                )
            ],

            [
                button(

                    text = "❌ لا أوافق",

                    callback = "decline"
                )
            ]

        ]
    }

# ==============================================
# 📜 CONSENT TEXT
# ==============================================

def consent_text() -> str:

    text = (

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

    logger.info(

        "display_consent_text",

        extra={
            "length": len(text)
        }
    )

    return text

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

                    text = "🔙 رجوع",

                    callback = "back_step"
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
                        "url": MAP_URL
                    }
                }
            ],

            [
                button(

                    text = "🔙 رجوع",

                    callback = "back_step"
                )
            ]

        ]
    }

# ==============================================
# 🍽️ RESTAURANTS UI
# ==============================================

def restaurants_ui(

    *,

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

                        text = "❌ لا توجد مطاعم",

                        callback = "noop"
                    )
                ],

                [
                    button(

                        text = "🔙 رجوع",

                        callback = "back_main"
                    )
                ]

            ]
        }

    # ==========================================
    # 🍔 RESTAURANTS
    # ==========================================

    buttons = []

    for restaurant in restaurants:

        restaurant = restaurant.get(

            "name",

            "Unknown"
        )

        restaurant_id = restaurant.get(

            "id",

            0
        )

        logger.debug(

            "processing_restaurant",

            extra={
                "restaurant_id": restaurant_id
            }
        )

        buttons.append(

            [

                button(

                    text = f"🍔 {restaurant}",

                    callback = f"rest_{restaurant_id}"
                )

            ]
        )

    # ==========================================
    # 🔙 BACK BUTTON
    # ==========================================

    buttons.append(

        [

            button(

                text = "🔙 رجوع",

                callback = "back_main"
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

    *,

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

                    text = "📦 طلب",

                    callback = f"order_{restaurant_id}"
                )
            ],

            [
                button(

                    text = "🔙 رجوع",

                    callback = "show_restaurants"
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

                    text = "1- مطعم تقليدي",

                    callback = "type_traditional"
                )
            ],

            [
                button(

                    text = "2- Fast Food",

                    callback = "type_fastfood"
                )
            ],

            [
                button(

                    text = "3- مشاوي",

                    callback = "type_grill"
                )
            ],

            [
                button(

                    text = "4- مطعم فاخر",

                    callback = "type_luxury"
                )
            ],

            [
                button(

                    text = "5- أكل شعبي",

                    callback = "type_popular"
                )
            ],

            [
                button(

                    text = "6- مقهى 24 ساعة",

                    callback = "type_cafe"
                )
            ],

            [
                button(

                    text = "7- حلويات",

                    callback = "type_sweets"
                )
            ],

            [
                button(

                    text = "🔙 رجوع",

                    callback = "back_main"
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

                    text = "✅ تأكيد التسجيل",

                    callback = "confirm"
                )
            ],

            [
                button(

                    text = "🔙 رجوع",

                    callback = "back_main"
                )
            ]

        ]
    }
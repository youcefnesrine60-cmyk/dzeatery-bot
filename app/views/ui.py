from app.repositories.restaurant_repo import get_all_restaurants

# =========================
# 🟢 UI BUILDERS
# =========================
def main_menu_ui():
    return {
        "inline_keyboard": [
            [{"text": "🍽️  زبون مطعم", "callback_data": "customer"}],
            [{"text": "🏪  صاحب محل", "callback_data": "owner"}]
        ]
    }

def consent_ui(role):
    return {
        "inline_keyboard": [
            [{"text": "✅ أوافق", "callback_data": f"consent_{role}"}],
            [{"text": "❌ لا أوافق", "callback_data": "decline"}]
        ]
    }

def consent_text():
    return (
        "📢 <b> إشعار قانوني/خاص بالدولة الجزائرية</b>\n\n"
        "<b><u> سياسة حماية المعطيات ذات الطابع الشخصي </u></b>\n\n"
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

def back_ui():
    return {
        "inline_keyboard": [
            [{"text": "🔙 رجوع", "callback_data": "back_step"}]
        ]
    }

def location_webapp_ui():
    return {
        "inline_keyboard": [
            [{
                "text": "📍 تحديد موقع المحل",
                "web_app": {
                    "url": "https://dzeatery.onrender.com/map"
                }
            }],
            [{"text": "🔙 رجوع", "callback_data": "back_step"}]
        ]
    }

def restaurants_ui():
    restaurants = get_all_restaurants()
    buttons = []

    for name in restaurants:
        buttons.append([{
            "text": f"🍔 {name}",
            "callback_data": f"rest_{name}"
        }])

    buttons.append([{"text": "🔙 رجوع", "callback_data": "back_main"}])
    return {"inline_keyboard": buttons}

def restaurant_actions_ui(name):
    return {
        "inline_keyboard": [
            [{"text": "📦 طلب", "callback_data": f"order_{name}"}],
            [{"text": "🔙 رجوع", "callback_data": "back_restaurants"}]
        ]
    }

def types_ui():
    return {
        "inline_keyboard": [
            [{"text": "1- مطعم تقليدي", "callback_data": "type_traditional"}],
            [{"text": "2- Fast Food", "callback_data": "type_fastfood"}],
            [{"text": "3- مشاوي", "callback_data": "type_grill"}],
            [{"text": "4- مطعم فاخر", "callback_data": "type_luxury"}],
            [{"text": "5- أكل شعبي", "callback_data": "type_popular"}],
            [{"text": "6- مقهى 24 ساعة", "callback_data": "type_cafe"}],
            [{"text": "7- حلويات", "callback_data": "type_sweets"}],
            [{"text": "🔙 رجوع", "callback_data": "back_main"}]
        ]
    }

def confirm_ui():
    return {
        "inline_keyboard": [
            [{"text": "✅ تأكيد التسجيل", "callback_data": "confirm"}],
            [{"text": "🔙 رجوع", "callback_data": "back_main"}]
        ]
    }
#======================================
# المسؤول عن:
# عرض المطاعم
# اختيار المطعم
#======================================

from app.helpers.ui_manager import (
    UIManager
)

from app.repositories.restaurant_repo import (
    get_all_restaurants
)

from app.views.ui import (
    restaurants_ui,
    restaurant_actions_ui
)

from app.core.logger import (
    logger
)

# =========== عرض المطاعم =============
async def show_restaurants(
    chat_id: int,
    message_id: int
) -> None:

    restaurants = get_all_restaurants()

    if not restaurants:

        logger.warning(
            "لا توجد مطاعم لعرضها للمستخدم",
            extra=
            {
                "chat_id": chat_id
            }
        )
        await UIManager.update(
            chat_id,
            message_id,
            "❌ عذراً، قائمة المطاعم غير متوفرة حالياً"
        )

        return

    await UIManager.update(
        chat_id,
        message_id,
        "🍽️ اختر مطعم:",
        restaurants_ui(restaurants)
    )

# =========== اختيار المطعم =============
async def handle_restaurant_selection(
    chat_id: int,
    message_id: int,
    callback_data: str
) -> None:

    name = callback_data.replace("rest_", "")

    await UIManager.update(
        chat_id,
        message_id,
        f"🍔 {name}",

        restaurant_actions_ui(name)
    )
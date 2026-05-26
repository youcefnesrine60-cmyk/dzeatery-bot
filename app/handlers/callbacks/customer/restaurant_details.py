# ==============================================
# 🍔 RESTAURANT DETAILS
# ==============================================

from app.helpers.ui_manager import (
    UIManager
)

from app.views.ui import (
    back_ui,
    restaurant_actions_ui
)

from app.repositories.restaurant_repo import (
    get_restaurant_by_id
)

from app.core.logger import (
    logger
)

# ==============================================
# 🍔 HANDLE RESTAURANT SELECTION
# ==============================================

async def handle_restaurant_selection(

    chat_id: int,

    message_id: int,

    callback_data: str

) -> None:

    # ==========================================
    # 🔍 EXTRACT RESTAURANT ID
    # ==========================================

    try:

        restaurant_id = int(

            callback_data.replace(

                "rest_",

                ""
            )
        )

    except ValueError:

        logger.warning(

            "invalid_restaurant_callback",

            extra={
                "chat_id": chat_id,
                "callback_data": callback_data
            }
        )

        return

    # ==========================================
    # 🔍 LOAD RESTAURANT
    # ==========================================

    restaurant = get_restaurant_by_id(

        restaurant_id
    )

    if not restaurant:

        logger.warning(

            "restaurant_not_found",

            extra={
                "chat_id": chat_id,
                "restaurant_id": restaurant_id
            }
        )

        await UIManager.update(

            chat_id = chat_id,

            text = "❌ المطعم غير موجود.",

            reply_markup = back_ui(),

            message_id = message_id
        )

        return

    # ==========================================
    # ✅ SUCCESS
    # ==========================================

    logger.info(

        "restaurant_selected",

        extra={
            "chat_id": chat_id,
            "restaurant_id": restaurant_id
        }
    )

    await UIManager.update(

        chat_id = chat_id,

        text = f"🍔 {restaurant['name']}",

        reply_markup = restaurant_actions_ui(
            restaurant_id
        ),

        message_id = message_id,
    )
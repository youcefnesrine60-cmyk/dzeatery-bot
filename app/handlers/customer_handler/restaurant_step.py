# ==============================================
# 🍽️ RESTAURANT STEP
# معالجة رسائل المستخدم أثناء اختيار المطعم
# ==============================================

from app.core.logger import logger

from app.helpers.ui_manager import UIManager
from app.repositories.state_repo import set_state
from app.repositories.restaurant_repo import get_restaurant_by_id
from app.repositories.products_repo import get_restaurant_products

from app.states.customer_states import CustomerStates


# ==============================================
# 🍽️ HANDLE RESTAURANT STEP
# ==============================================

async def handle_restaurant_step(
    *,
    chat_id: int,
    text: str,
    state: dict,
) -> None:
    """
    معالجة رسائل المستخدم في مرحلة اختيار المطعم
    
    يقوم المستخدم بإدخال رقم المطعم، ثم نقوم بـ:
    1. التحقق من صحة الرقم
    2. جلب بيانات المطعم من قاعدة البيانات
    3. جلب قائمة المنتجات الخاصة بالمطعم
    4. حفظ البيانات في الحالة
    5. عرض قائمة المنتجات للمستخدم
    
    Args:
        chat_id: معرف المستخدم
        text: النص المرسل (رقم المطعم)
        state: حالة المستخدم الحالية
    """
    logger.info(
        "handle_restaurant_step",
        extra={
            "chat_id": chat_id,
            "text_length": len(text),
        },
    )

    # ==========================================
    # 1️⃣ التحقق من صحة الإدخال
    # ==========================================

    try:
        restaurant_id = int(text.strip())
    except ValueError:
        logger.warning(
            "restaurant_step_invalid_input",
            extra={
                "chat_id": chat_id,
                "text": text,
            },
        )

        await UIManager.update(
            chat_id=chat_id,
            text="❌ الرجاء إدخال رقم المطعم الصحيح.",
            reply_markup=None,
        )
        return

    # ==========================================
    # 2️⃣ جلب بيانات المطعم
    # ==========================================

    restaurant = await get_restaurant_by_id(
        restaurant_id=restaurant_id,
    )

    if not restaurant:
        logger.warning(
            "restaurant_step_not_found",
            extra={
                "chat_id": chat_id,
                "restaurant_id": restaurant_id,
            },
        )

        await UIManager.update(
            chat_id=chat_id,
            text="❌ المطعم غير موجود.",
            reply_markup=None,
        )
        return

    # ==========================================
    # 3️⃣ جلب قائمة المنتجات
    # ==========================================

    products = await get_restaurant_products(
        restaurant_id=restaurant_id,
    )

    # ==========================================
    # 4️⃣ حفظ البيانات في الحالة
    # ==========================================

    state["restaurant_id"] = restaurant_id
    state["restaurant_name"] = restaurant.get("name")
    state["products"] = products

    # الانتقال إلى مرحلة المنتجات
    state["step"] = CustomerStates.PRODUCT

    # حفظ الحالة
    await set_state(
        chat_id=chat_id,
        state=state,
    )

    logger.info(
        "restaurant_selected",
        extra={
            "chat_id": chat_id,
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.get("name"),
            "products_count": len(products) if products else 0,
        },
    )

    # ==========================================
    # 5️⃣ عرض قائمة المنتجات للمستخدم
    # ==========================================

    if not products:
        text_message = (
            f"🍔 {restaurant.get('name')}\n\n"
            f"⚠️ لا توجد منتجات متاحة حالياً."
        )
    else:
        # بناء قائمة المنتجات بشكل منظم
        products_text = "\n".join(
            f"{p.get('id')}. {p.get('name')} - {p.get('price')} دج"
            for p in products
        )

        text_message = (
            f"🍔 {restaurant.get('name')}\n\n"
            f"📋 اختر المنتج الذي تريده بإدخال رقمه:\n\n"
            f"{products_text}\n\n"
            f"💡 يمكنك اختيار عدة منتجات، ثم الذهاب إلى السلة."
        )

    await UIManager.update(
        chat_id=chat_id,
        text=text_message,
        reply_markup=None,
    )
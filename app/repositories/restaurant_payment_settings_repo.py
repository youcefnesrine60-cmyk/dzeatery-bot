# ==============================================
# 🏦 RESTAURANT PAYMENT SETTINGS REPOSITORY
# Async Psycopg3 Version
# ==============================================

from app.core.db import (
    execute,
    fetchrow,
    insert_returning_id,
)
from app.core.logger import logger

# ==============================================
# 🔍 GET PAYMENT SETTINGS
# ==============================================

async def get_restaurant_payment_settings(
    *,
    restaurant_id: int,
) -> dict | None:
    """
    جلب إعدادات الدفع لمطعم معين
    
    Args:
        restaurant_id: معرف المطعم
        
    Returns:
        dict | None: إعدادات الدفع أو None
    """
    row = await fetchrow(
        """
        SELECT
            id,
            restaurant_id,
            allow_cash,
            allow_card,
            allow_ccp,
            allow_baridimob,
            allow_stripe,
            allow_paypal,
            created_at,
            updated_at
        FROM restaurant_payment_settings
        WHERE restaurant_id = %s
        """,
        restaurant_id,
    )
    
    if not row:
        return None
    
    return {
        "id": row["id"],
        "restaurant_id": row["restaurant_id"],
        "allow_cash": row["allow_cash"],
        "allow_card": row["allow_card"],
        "allow_ccp": row["allow_ccp"],
        "allow_baridimob": row["allow_baridimob"],
        "allow_stripe": row["allow_stripe"],
        "allow_paypal": row["allow_paypal"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

# ==============================================
# ➕ CREATE OR UPDATE PAYMENT SETTINGS
# ==============================================

async def upsert_restaurant_payment_settings(
    *,
    restaurant_id: int,
    allow_cash: bool = True,
    allow_card: bool = True,
    allow_ccp: bool = False,
    allow_baridimob: bool = False,
    allow_stripe: bool = False,
    allow_paypal: bool = False,
) -> dict:
    """
    إنشاء أو تحديث إعدادات الدفع لمطعم
    
    Args:
        restaurant_id: معرف المطعم
        allow_cash: السماح بالدفع نقداً
        allow_card: السماح بالدفع ببطاقة POS
        allow_ccp: السماح بالدفع عبر CCP
        allow_baridimob: السماح بالدفع عبر بريدي موب
        allow_stripe: السماح بالدفع عبر Stripe
        allow_paypal: السماح بالدفع عبر PayPal
        
    Returns:
        dict: إعدادات الدفع المحدثة
    """
    # محاولة تحديث الإعدادات الموجودة
    existing = await get_restaurant_payment_settings(
        restaurant_id=restaurant_id,
    )

    if existing:
        # تحديث الإعدادات الموجودة
        await execute(
            """
            UPDATE restaurant_payment_settings
            SET
                allow_cash = %s,
                allow_card = %s,
                allow_ccp = %s,
                allow_baridimob = %s,
                allow_stripe = %s,
                allow_paypal = %s,
                updated_at = NOW()
            WHERE restaurant_id = %s
            RETURNING
                id,
                restaurant_id,
                allow_cash,
                allow_card,
                allow_ccp,
                allow_baridimob,
                allow_stripe,
                allow_paypal,
                created_at,
                updated_at
            """,
            allow_cash,
            allow_card,
            allow_ccp,
            allow_baridimob,
            allow_stripe,
            allow_paypal,
            restaurant_id,
        )

        # جلب الإعدادات المحدثة
        return await get_restaurant_payment_settings(
            restaurant_id=restaurant_id,
        )

    # إنشاء إعدادات جديدة
    payment_id = await insert_returning_id(
        """
        INSERT INTO restaurant_payment_settings
        (
            restaurant_id,
            allow_cash,
            allow_card,
            allow_ccp,
            allow_baridimob,
            allow_stripe,
            allow_paypal
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        restaurant_id,
        allow_cash,
        allow_card,
        allow_ccp,
        allow_baridimob,
        allow_stripe,
        allow_paypal,
    )

    logger.info(
        "restaurant_payment_settings_created",
        extra={
            "payment_id": payment_id,
            "restaurant_id": restaurant_id,
        },
    )

    # جلب الإعدادات المنشأة
    return await get_restaurant_payment_settings(
        restaurant_id=restaurant_id,
    )
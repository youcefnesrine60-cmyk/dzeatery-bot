# ==============================================
# 💰 PRICING SERVICE
# Dz-Eatery Pricing Engine
# Async Compatible Version
# ==============================================

from decimal import Decimal

from app.repositories.subscription_plan_repo import get_subscription_plan_by_id
from app.repositories.feature_pricing_repo import get_feature_pricing
from app.repositories.loyalty_discount_repo import get_loyalty_discount_for_years
from app.repositories.multi_restaurant_discount_repo import get_multi_restaurant_discount_for_count
from app.repositories.branch_pricing_repo import get_branch_pricing_rule
from app.repositories.promotion_repo import get_active_promotion

# ==============================================
# CONSTANTS
# ==============================================

PAYMENT_CASH = "cash"
PAYMENT_ELECTRONIC = "electronic"

MONTHLY = "monthly"
YEARLY = "yearly"

# ==============================================
# RESTAURANT SCORE
# ==============================================

def calculate_restaurant_score(
    *,
    products_count: int,
    categories_count: int,
    monthly_orders: int,
    average_order_value: float,
) -> Decimal:

    score = (
        (
            products_count * 1
            + categories_count * 3
            + monthly_orders * 0.1
            + (average_order_value / 100)
        )
        * 10
    )

    return Decimal(str(round(score, 2)))

# ==============================================
# ADDITIONAL FEATURES PRICE
# ==============================================

async def calculate_additional_features_price(
    *,
    feature_ids: list[int],
    billing_cycle: str,
) -> Decimal:

    total = Decimal("0")

    for feature_id in feature_ids:

        feature_price = await get_feature_pricing(
            feature_id=feature_id,
            billing_cycle=billing_cycle,
        )

        if not feature_price:
            continue

        total += Decimal(str(feature_price["price"]))

    return total

# ==============================================
# PLAN BASE PRICE
# ==============================================

async def calculate_plan_base_price(
    *,
    plan_id: int,
    billing_cycle: str,
    additional_feature_ids: list[int] | None = None,
) -> Decimal:

    additional_feature_ids = additional_feature_ids or []

    plan = await get_subscription_plan_by_id(
        plan_id=plan_id,
    )

    if not plan:
        raise ValueError("plan_not_found")

    base_price = Decimal(str(plan["base_price"]))
    discount_percent = Decimal(str(plan["plan_discount_percent"]))

    additional_features_price = await calculate_additional_features_price(
        feature_ids=additional_feature_ids,
        billing_cycle=billing_cycle,
    )

    discounted_features_price = (
        additional_features_price
        * (Decimal("100") - discount_percent)
        / Decimal("100")
    )

    return base_price + discounted_features_price

# ==============================================
# LOYALTY DISCOUNT
# ==============================================

async def calculate_loyalty_discount(
    *,
    years_with_platform: int,
    amount: Decimal,
) -> Decimal:

    percent = await get_loyalty_discount_for_years(
        years=years_with_platform,
    )

    if not percent:
        return Decimal("0")

    return amount * Decimal(str(percent)) / Decimal("100")

# ==============================================
# MULTI RESTAURANT DISCOUNT
# ==============================================

async def calculate_multi_restaurant_discount(
    *,
    restaurants_count: int,
    amount: Decimal,
) -> Decimal:

    rule = await get_multi_restaurant_discount_for_count(
        restaurants_count=restaurants_count,
    )

    if not rule:
        return Decimal("0")

    return amount * Decimal(str(rule["discount_percent"])) / Decimal("100")

# ==============================================
# PROMOTION DISCOUNT
# ==============================================

async def calculate_promotion_discount(
    *,
    amount: Decimal,
) -> Decimal:

    promotion = await get_active_promotion()

    if not promotion:
        return Decimal("0")

    return amount * Decimal(str(promotion["discount_percent"])) / Decimal("100")

# ==============================================
# MULTI BRANCH COST
# ==============================================

async def calculate_multi_branch_cost(
    *,
    branches_count: int,
) -> Decimal:

    if branches_count <= 1:
        return Decimal("0")

    rule = await get_branch_pricing_rule(
        branches_count=branches_count,
    )

    if not rule:
        return Decimal("0")

    price_per_branch = Decimal(str(rule["price_per_branch"]))
    additional_branches = branches_count - 1

    return price_per_branch * additional_branches

# ==============================================
# BILLING CYCLE MULTIPLIER
# ==============================================

def calculate_billing_cycle_price(
    *,
    amount: Decimal,
    billing_cycle: str,
) -> Decimal:

    if billing_cycle == MONTHLY:
        return amount

    if billing_cycle == YEARLY:
        return amount * Decimal("10")

    raise ValueError("invalid_billing_cycle")

# ==============================================
# PAYMENT ADJUSTMENT
# ==============================================

def calculate_payment_adjustment(
    *,
    amount: Decimal,
    payment_method: str,
) -> Decimal:

    if payment_method == PAYMENT_ELECTRONIC:
        return amount * Decimal("-2") / Decimal("100")

    if payment_method == PAYMENT_CASH:
        return amount * Decimal("2") / Decimal("100")

    return Decimal("0")

# ==============================================
# FINAL PRICING
# ==============================================

async def calculate_subscription_pricing(
    *,
    plan_id: int,
    billing_cycle: str,
    payment_method: str,
    restaurants_count: int,
    branches_count: int,
    years_with_platform: int,
    products_count: int,
    categories_count: int,
    monthly_orders: int,
    average_order_value: float,
    additional_feature_ids: list[int] | None = None,
) -> dict[str, object]:

    additional_feature_ids = additional_feature_ids or []

    base_price = await calculate_plan_base_price(
        plan_id=plan_id,
        billing_cycle=billing_cycle,
        additional_feature_ids=additional_feature_ids,
    )

    restaurant_score = calculate_restaurant_score(
        products_count=products_count,
        categories_count=categories_count,
        monthly_orders=monthly_orders,
        average_order_value=average_order_value,
    )

    value_before_discounts = base_price + restaurant_score

    loyalty_discount = await calculate_loyalty_discount(
        years_with_platform=years_with_platform,
        amount=value_before_discounts,
    )

    multi_restaurant_discount = await calculate_multi_restaurant_discount(
        restaurants_count=restaurants_count,
        amount=value_before_discounts,
    )

    promotion_discount = await calculate_promotion_discount(
        amount=value_before_discounts,
    )

    total_discount = (
        loyalty_discount
        + multi_restaurant_discount
        + promotion_discount
    )

    branch_cost = await calculate_multi_branch_cost(
        branches_count=branches_count,
    )

    final_price = value_before_discounts - total_discount + branch_cost

    final_price = calculate_billing_cycle_price(
        amount=final_price,
        billing_cycle=billing_cycle,
    )

    payment_adjustment = calculate_payment_adjustment(
        amount=final_price,
        payment_method=payment_method,
    )

    final_amount_due = final_price + payment_adjustment

    return {
        "base_price": float(base_price),
        "restaurant_score": float(restaurant_score),
        "value_before_discounts": float(value_before_discounts),
        "loyalty_discount": float(loyalty_discount),
        "multi_restaurant_discount": float(multi_restaurant_discount),
        "promotion_discount": float(promotion_discount),
        "discount_price": float(total_discount),
        "multi_branch_cost": float(branch_cost),
        "final_price": float(final_price),
        "payment_adjustment": float(payment_adjustment),
        "final_amount_due": float(final_amount_due),
    }
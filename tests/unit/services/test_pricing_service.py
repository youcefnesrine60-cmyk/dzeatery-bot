# ==============================================
# 🧪 TEST PRICING SERVICE
# ==============================================

import pytest
from decimal import Decimal
from unittest.mock import patch

from app.services.business.pricing_service import (
    calculate_restaurant_score,
    calculate_subscription_pricing,
)


@pytest.mark.asyncio
async def test_calculate_restaurant_score():
    """
    اختبار حساب حجم المطعم
    """
    score = calculate_restaurant_score(
        products_count=10,
        categories_count=3,
        monthly_orders=50,
        average_order_value=200,
    )

    expected_score = Decimal(str(round(((10 * 1 + 3 * 3 + 50 * 0.1 + (200 / 100)) * 10), 2)))
    assert score == expected_score


@pytest.mark.asyncio
async def test_calculate_subscription_pricing_basic():
    """
    اختبار حساب سعر الباقة الأساسية
    """
    with patch("app.services.business.pricing_service.get_subscription_plan_by_id") as mock_plan:
        mock_plan.return_value = {
            "id": 1,
            "code": "basic",
            "name": "Basic",
            "base_price": 3000,
            "plan_discount_percent": 0,
        }

        with patch("app.services.business.pricing_service.get_feature_pricing") as mock_feature:
            mock_feature.return_value = None

            with patch("app.services.business.pricing_service.get_loyalty_discount_for_years") as mock_loyalty:
                mock_loyalty.return_value = 0

                with patch("app.services.business.pricing_service.get_multi_restaurant_discount_for_count") as mock_multi:
                    mock_multi.return_value = None

                    with patch("app.services.business.pricing_service.get_active_promotion") as mock_promo:
                        mock_promo.return_value = None

                        with patch("app.services.business.pricing_service.get_branch_pricing_rule") as mock_branch:
                            mock_branch.return_value = None

                            result = await calculate_subscription_pricing(
                                plan_id=1,
                                billing_cycle="monthly",
                                payment_method="electronic",
                                restaurants_count=1,
                                branches_count=1,
                                years_with_platform=0,
                                products_count=0,
                                categories_count=0,
                                monthly_orders=0,
                                average_order_value=0,
                            )

                            assert result["base_price"] == 3000
                            assert result["final_amount_due"] > 0


@pytest.mark.asyncio
async def test_calculate_subscription_pricing_with_discounts():
    """
    اختبار حساب السعر مع جميع الخصومات
    """
    with patch("app.services.business.pricing_service.get_subscription_plan_by_id") as mock_plan:
        mock_plan.return_value = {
            "id": 1,
            "code": "professional",
            "base_price": 5000,
            "plan_discount_percent": 5,
        }

        with patch("app.services.business.pricing_service.get_feature_pricing") as mock_feature:
            mock_feature.return_value = {"price": 500}

            with patch("app.services.business.pricing_service.get_loyalty_discount_for_years") as mock_loyalty:
                mock_loyalty.return_value = 5  # 5% خصم الولاء

                with patch("app.services.business.pricing_service.get_multi_restaurant_discount_for_count") as mock_multi:
                    mock_multi.return_value = {"discount_percent": 5}

                    with patch("app.services.business.pricing_service.get_active_promotion") as mock_promo:
                        mock_promo.return_value = {"discount_percent": 10}

                        with patch("app.services.business.pricing_service.get_branch_pricing_rule") as mock_branch:
                            mock_branch.return_value = {"price_per_branch": 500}

                            result = await calculate_subscription_pricing(
                                plan_id=1,
                                billing_cycle="monthly",
                                payment_method="electronic",
                                restaurants_count=3,
                                branches_count=2,
                                years_with_platform=3,
                                products_count=10,
                                categories_count=3,
                                monthly_orders=50,
                                average_order_value=200,
                            )

                            assert result["base_price"] > 0
                            assert result["loyalty_discount"] > 0
                            assert result["multi_restaurant_discount"] > 0
                            assert result["promotion_discount"] > 0
                            assert result["multi_branch_cost"] > 0


@pytest.mark.asyncio
async def test_calculate_subscription_pricing_yearly():
    """
    اختبار حساب السعر السنوي
    """
    with patch("app.services.business.pricing_service.get_subscription_plan_by_id") as mock_plan:
        mock_plan.return_value = {
            "id": 1,
            "code": "basic",
            "base_price": 3000,
            "plan_discount_percent": 0,
        }

        with patch("app.services.business.pricing_service.get_feature_pricing") as mock_feature:
            mock_feature.return_value = None

            with patch("app.services.business.pricing_service.get_loyalty_discount_for_years") as mock_loyalty:
                mock_loyalty.return_value = 0

                with patch("app.services.business.pricing_service.get_multi_restaurant_discount_for_count") as mock_multi:
                    mock_multi.return_value = None

                    with patch("app.services.business.pricing_service.get_active_promotion") as mock_promo:
                        mock_promo.return_value = None

                        with patch("app.services.business.pricing_service.get_branch_pricing_rule") as mock_branch:
                            mock_branch.return_value = None

                            result = await calculate_subscription_pricing(
                                plan_id=1,
                                billing_cycle="yearly",  # سنوي
                                payment_method="electronic",
                                restaurants_count=1,
                                branches_count=1,
                                years_with_platform=0,
                                products_count=0,
                                categories_count=0,
                                monthly_orders=0,
                                average_order_value=0,
                            )

                            # ✅ السعر السنوي = 3000 * 10 = 30000 - 2% خصم الدفع الإلكتروني = 29400
                            assert result["final_amount_due"] == 29400.0
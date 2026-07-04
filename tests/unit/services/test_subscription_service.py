# ==============================================
# 🧪 TEST SUBSCRIPTION SERVICE
# ==============================================

import pytest
from unittest.mock import AsyncMock, patch

from app.services.business.subscription_service import (
    create_trial_subscription,
    preview_subscription_pricing,
)


@pytest.mark.asyncio
async def test_create_trial_subscription_success():
    """
    اختبار إنشاء اشتراك تجريبي
    """
    with patch("app.services.business.subscription_service.has_used_trial") as mock_has_trial:
        mock_has_trial.return_value = False

        with patch("app.services.business.subscription_service.get_subscription_plan_by_code") as mock_plan:
            mock_plan.return_value = {
                "id": 1,
                "code": "trial",
                "name": "Trial",
            }

            with patch("app.services.business.subscription_service.create_subscription") as mock_sub:
                mock_sub.return_value = 1

                with patch("app.services.business.subscription_service.get_plan_features") as mock_features:
                    mock_features.return_value = [
                        {"feature_id": 1},
                        {"feature_id": 2},
                    ]

                    with patch("app.services.business.subscription_service.create_subscription_feature") as mock_feature:
                        with patch("app.services.business.subscription_service.mark_trial_used") as mock_mark:

                            subscription_id = await create_trial_subscription(
                                owner_id=1,
                                restaurant_id=1,
                            )

                            assert subscription_id == 1


@pytest.mark.asyncio
async def test_create_trial_subscription_already_used():
    """
    اختبار إنشاء اشتراك تجريبي عند استخدامه مسبقاً
    """
    with patch("app.services.business.subscription_service.has_used_trial") as mock_has_trial:
        mock_has_trial.return_value = True

        with pytest.raises(ValueError) as exc:
            await create_trial_subscription(
                owner_id=1,
                restaurant_id=1,
            )

        assert str(exc.value) == "trial_already_used"


@pytest.mark.asyncio
async def test_preview_subscription_pricing_success():
    """
    اختبار عرض سعر الاشتراك
    """
    # ✅ استخدام AsyncMock مع return_value
    mock_calc = AsyncMock()
    mock_calc.return_value = {
        "base_price": 3000,
        "restaurant_score": 50,
        "final_amount_due": 3050,
    }

    with patch(
        "app.services.business.subscription_service.calculate_subscription_pricing",
        mock_calc
    ):
        result = await preview_subscription_pricing(
            plan_id=1,
            billing_cycle="monthly",
            payment_method="electronic",
            restaurants_count=1,
            branches_count=1,
            years_with_platform=0,
            products_count=10,
            categories_count=3,
            monthly_orders=0,
            average_order_value=0,
        )

        assert result["base_price"] == 3000
        assert result["final_amount_due"] == 3050
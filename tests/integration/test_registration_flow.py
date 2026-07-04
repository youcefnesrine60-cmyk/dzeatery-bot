# ==============================================
# 🧪 TEST REGISTRATION FLOW
# اختبار تدفق التسجيل الكامل
# ==============================================

import pytest
from unittest.mock import AsyncMock, patch

from app.services.business.registration_service import approve_registration
from app.repositories.registration_request_repo import create_registration_request


@pytest.mark.asyncio
async def test_registration_flow_success():
    """
    اختبار تدفق التسجيل الكامل (إنشاء طلب ← موافقة ← إنشاء مالك ← إنشاء مطعم)
    """
    # 1️⃣ إنشاء طلب تسجيل
    with patch("app.repositories.registration_request_repo.insert_returning_id") as mock_insert:
        mock_insert.return_value = 1

        request_id = await create_registration_request(
            chat_id=123456789,
            full_name="أحمد محمد",
            owner_phone="0555123456",
            email="ahmed@example.com",
            restaurant_name="مطعم النخبة",
            restaurant_type="traditional",
            restaurant_phone="0555123456",
            wilaya="الجزائر",
            lat=36.75,
            lng=3.06,
        )

        assert request_id == 1

    # 2️⃣ الموافقة على الطلب
    with patch("app.services.business.registration_service.get_registration_request_by_id") as mock_get:
        mock_get.return_value = {
            "id": 1,
            "chat_id": 123456789,
            "full_name": "أحمد محمد",
            "owner_phone": "0555123456",
            "email": "ahmed@example.com",
            "restaurant_name": "مطعم النخبة",
            "restaurant_type": "traditional",
            "restaurant_phone": "0555123456",
            "wilaya": "الجزائر",
            "lat": 36.75,
            "lng": 3.06,
        }

        with patch("app.services.business.registration_service.get_or_create_owner") as mock_owner:
            mock_owner.return_value = 1

            with patch("app.services.business.registration_service.create_restaurant") as mock_restaurant:
                mock_restaurant.return_value = 1

                with patch("app.services.business.registration_service.create_restaurant_metrics") as mock_metrics:
                    with patch("app.services.business.registration_service.create_trial_subscription") as mock_subscription:
                        mock_subscription.return_value = 1

                        with patch("app.services.business.registration_service.approve_owner"):
                            with patch("app.services.business.registration_service.approve_registration_request"):

                                result = await approve_registration(request_id=1)

                                assert result["owner_id"] == 1
                                assert result["restaurant_id"] == 1
                                assert result["subscription_id"] == 1
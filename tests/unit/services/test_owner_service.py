# ==============================================
# 🧪 TEST OWNER SERVICE
# ==============================================

import pytest
from unittest.mock import patch

from app.services.business.owner_service import (
    get_or_create_owner,
    can_use_trial,
    approve_owner,
)


@pytest.mark.asyncio
async def test_get_or_create_owner_exists():
    """
    اختبار جلب مالك موجود
    """
    with patch("app.services.business.owner_service.get_owner_by_chat_id") as mock_get:
        mock_get.return_value = {"id": 1, "chat_id": 123456789}

        owner_id = await get_or_create_owner(
            chat_id=123456789,
            full_name="أحمد محمد",
            phone="0555123456",
            email="ahmed@example.com",
        )

        assert owner_id == 1


@pytest.mark.asyncio
async def test_get_or_create_owner_new():
    """
    اختبار إنشاء مالك جديد
    """
    with patch("app.services.business.owner_service.get_owner_by_chat_id") as mock_get:
        mock_get.return_value = None

        with patch("app.services.business.owner_service.create_owner") as mock_create:
            mock_create.return_value = 2

            owner_id = await get_or_create_owner(
                chat_id=123456789,
                full_name="أحمد محمد",
                phone="0555123456",
                email="ahmed@example.com",
            )

            assert owner_id == 2


@pytest.mark.asyncio
async def test_can_use_trial_true():
    """
    اختبار إمكانية استخدام التجربة المجانية
    """
    with patch("app.services.business.owner_service.has_used_trial") as mock_has:
        mock_has.return_value = False

        result = await can_use_trial(owner_id=1)

        assert result is True


@pytest.mark.asyncio
async def test_can_use_trial_false():
    """
    اختبار عدم إمكانية استخدام التجربة المجانية
    """
    with patch("app.services.business.owner_service.has_used_trial") as mock_has:
        mock_has.return_value = True

        result = await can_use_trial(owner_id=1)

        assert result is False


@pytest.mark.asyncio
async def test_approve_owner_success():
    """
    اختبار الموافقة على مالك
    """
    with patch("app.services.business.owner_service.update_registration_status") as mock_update:
        await approve_owner(owner_id=1)

        mock_update.assert_called_once_with(
            owner_id=1,
            status="approved",
        )
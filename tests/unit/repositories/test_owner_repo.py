# ==============================================
# 🧪 TEST OWNER REPOSITORY
# ==============================================

import pytest
from unittest.mock import AsyncMock, patch

from app.repositories.owner_repo import (
    create_owner,
    get_owner_by_chat_id,
    owner_exists,
)


@pytest.mark.asyncio
async def test_create_owner_success(mock_db):
    """
    اختبار إنشاء مالك جديد بنجاح
    """
    with patch("app.repositories.owner_repo.insert_returning_id") as mock_insert:
        mock_insert.return_value = 1

        owner_id = await create_owner(
            chat_id=123456789,
            full_name="أحمد محمد",
            phone="0555123456",
            email="ahmed@example.com",
        )

        assert owner_id == 1
        mock_insert.assert_called_once()


@pytest.mark.asyncio
async def test_get_owner_by_chat_id_success():
    """
    اختبار جلب مالك عن طريق chat_id
    """
    with patch("app.repositories.owner_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = {
            "id": 1,
            "chat_id": 123456789,
            "full_name": "أحمد محمد",
            "phone": "0555123456",
            "email": "ahmed@example.com",
        }

        owner = await get_owner_by_chat_id(chat_id=123456789)

        assert owner is not None
        assert owner["id"] == 1
        assert owner["full_name"] == "أحمد محمد"


@pytest.mark.asyncio
async def test_owner_exists_true():
    """
    اختبار التحقق من وجود مالك (موجود)
    """
    with patch("app.repositories.owner_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = {"1": 1}

        exists = await owner_exists(chat_id=123456789)

        assert exists is True


@pytest.mark.asyncio
async def test_owner_exists_false():
    """
    اختبار التحقق من وجود مالك (غير موجود)
    """
    with patch("app.repositories.owner_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = None

        exists = await owner_exists(chat_id=999999999)

        assert exists is False
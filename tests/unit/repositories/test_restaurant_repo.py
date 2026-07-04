# ==============================================
# 🧪 TEST RESTAURANT REPOSITORY
# ==============================================

import pytest
from unittest.mock import AsyncMock, patch

from app.repositories.restaurant_repo import (
    create_restaurant,
    get_restaurant_by_id,
    get_restaurants_by_owner,
    restaurant_exists_for_owner,
    get_all_restaurants,
)


@pytest.mark.asyncio
async def test_create_restaurant_success():
    """
    اختبار إنشاء مطعم جديد بنجاح
    """
    with patch("app.repositories.restaurant_repo.insert_returning_id") as mock_insert:
        mock_insert.return_value = 1

        restaurant_id = await create_restaurant(
            owner_id=1,
            name="مطعم النخبة",
            restaurant_type="traditional",
            phone="0555123456",
            wilaya="الجزائر",
            lat=36.75,
            lng=3.06,
        )

        assert restaurant_id == 1
        mock_insert.assert_called_once()


@pytest.mark.asyncio
async def test_get_restaurant_by_id_success():
    """
    اختبار جلب مطعم عن طريق المعرف
    """
    with patch("app.repositories.restaurant_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = {
            "id": 1,
            "owner_id": 1,
            "name": "مطعم النخبة",
            "type": "traditional",
            "phone": "0555123456",
            "wilaya": "الجزائر",
            "lat": 36.75,
            "lng": 3.06,
        }

        restaurant = await get_restaurant_by_id(restaurant_id=1)

        assert restaurant is not None
        assert restaurant["id"] == 1
        assert restaurant["name"] == "مطعم النخبة"


@pytest.mark.asyncio
async def test_get_restaurant_by_id_not_found():
    """
    اختبار جلب مطعم غير موجود
    """
    with patch("app.repositories.restaurant_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = None

        restaurant = await get_restaurant_by_id(restaurant_id=999)

        assert restaurant is None


@pytest.mark.asyncio
async def test_get_restaurants_by_owner_success():
    """
    اختبار جلب مطاعم مالك معين
    """
    # ✅ إضافة جميع الحقول المطلوبة
    with patch("app.repositories.restaurant_repo.fetch") as mock_fetch:
        mock_fetch.return_value = [
            {
                "id": 1,
                "owner_id": 1,
                "name": "مطعم 1",
                "type": "traditional",
                "phone": "0555123456",
                "wilaya": "الجزائر",
                "lat": 36.75,
                "lng": 3.06,
            },
            {
                "id": 2,
                "owner_id": 1,
                "name": "مطعم 2",
                "type": "fastfood",
                "phone": "0555123457",
                "wilaya": "وهران",
                "lat": 35.70,
                "lng": -0.63,
            },
        ]

        restaurants = await get_restaurants_by_owner(owner_id=1)

        assert len(restaurants) == 2
        assert restaurants[0]["id"] == 1
        assert restaurants[1]["id"] == 2


@pytest.mark.asyncio
async def test_restaurant_exists_for_owner_true():
    """
    اختبار التحقق من وجود مطعم لمالك معين (موجود)
    """
    with patch("app.repositories.restaurant_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = {"1": 1}

        exists = await restaurant_exists_for_owner(
            owner_id=1,
            name="مطعم النخبة",
            phone="0555123456",
            wilaya="الجزائر",
            lat=36.75,
            lng=3.06,
        )

        assert exists is True


@pytest.mark.asyncio
async def test_restaurant_exists_for_owner_false():
    """
    اختبار التحقق من وجود مطعم لمالك معين (غير موجود)
    """
    with patch("app.repositories.restaurant_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = None

        exists = await restaurant_exists_for_owner(
            owner_id=1,
            name="مطعم غير موجود",
            phone="0555123456",
            wilaya="الجزائر",
            lat=36.75,
            lng=3.06,
        )

        assert exists is False


@pytest.mark.asyncio
async def test_get_all_restaurants_success():
    """
    اختبار جلب جميع المطاعم
    """
    # ✅ إضافة جميع الحقول المطلوبة
    with patch("app.repositories.restaurant_repo.fetch") as mock_fetch:
        mock_fetch.return_value = [
            {
                "id": 1,
                "owner_id": 1,
                "name": "مطعم 1",
                "type": "traditional",
                "phone": "0555123456",
                "wilaya": "الجزائر",
                "lat": 36.75,
                "lng": 3.06,
            },
            {
                "id": 2,
                "owner_id": 2,
                "name": "مطعم 2",
                "type": "fastfood",
                "phone": "0555123457",
                "wilaya": "وهران",
                "lat": 35.70,
                "lng": -0.63,
            },
            {
                "id": 3,
                "owner_id": 3,
                "name": "مطعم 3",
                "type": "grill",
                "phone": "0555123458",
                "wilaya": "قسنطينة",
                "lat": 36.37,
                "lng": 6.61,
            },
        ]

        restaurants = await get_all_restaurants()

        assert len(restaurants) == 3
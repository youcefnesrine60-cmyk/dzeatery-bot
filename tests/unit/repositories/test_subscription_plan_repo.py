# ==============================================
# 🧪 TEST SUBSCRIPTION PLAN REPOSITORY
# ==============================================

import pytest
from datetime import datetime
from unittest.mock import patch

from app.repositories.subscription_plan_repo import (
    create_subscription_plan,
    get_subscription_plan_by_id,
    get_subscription_plan_by_code,
    get_active_subscription_plans,
    calculate_plan_price,
)


@pytest.mark.asyncio
async def test_create_subscription_plan_success():
    """
    اختبار إنشاء باقة اشتراك جديدة
    """
    with patch("app.repositories.subscription_plan_repo.insert_returning_id") as mock_insert:
        mock_insert.return_value = 1

        plan_id = await create_subscription_plan(
            code="basic",
            name="Basic",
            base_price=3000,
            plan_discount_percent=0,
        )

        assert plan_id == 1


@pytest.mark.asyncio
async def test_get_subscription_plan_by_id_success():
    """
    اختبار جلب باقة عن طريق المعرف
    """
    # ✅ إضافة جميع الحقول المطلوبة
    with patch("app.repositories.subscription_plan_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = {
            "id": 1,
            "code": "basic",
            "name": "Basic",
            "active": True,
            "created_at": datetime.now(),
            "plan_discount_percent": 0,
            "display_order": 1,
            "description": "الباقة الأساسية",
            "base_price": 3000,
        }

        plan = await get_subscription_plan_by_id(plan_id=1)

        assert plan is not None
        assert plan["code"] == "basic"
        assert plan["base_price"] == 3000


@pytest.mark.asyncio
async def test_get_subscription_plan_by_code_success():
    """
    اختبار جلب باقة عن طريق الكود
    """
    # ✅ إضافة جميع الحقول المطلوبة
    with patch("app.repositories.subscription_plan_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = {
            "id": 1,
            "code": "basic",
            "name": "Basic",
            "active": True,
            "created_at": datetime.now(),
            "plan_discount_percent": 0,
            "display_order": 1,
            "description": "الباقة الأساسية",
            "base_price": 3000,
        }

        plan = await get_subscription_plan_by_code(code="basic")

        assert plan is not None
        assert plan["code"] == "basic"


@pytest.mark.asyncio
async def test_get_active_subscription_plans_success():
    """
    اختبار جلب الباقات النشطة
    """
    # ✅ إضافة جميع الحقول المطلوبة
    with patch("app.repositories.subscription_plan_repo.fetch") as mock_fetch:
        mock_fetch.return_value = [
            {
                "id": 1,
                "code": "basic",
                "name": "Basic",
                "active": True,
                "created_at": datetime.now(),
                "plan_discount_percent": 0,
                "display_order": 1,
                "description": "الباقة الأساسية",
                "base_price": 3000,
            },
            {
                "id": 2,
                "code": "professional",
                "name": "Professional",
                "active": True,
                "created_at": datetime.now(),
                "plan_discount_percent": 5,
                "display_order": 2,
                "description": "الباقة الاحترافية",
                "base_price": 5000,
            },
            {
                "id": 3,
                "code": "enterprise",
                "name": "Enterprise",
                "active": True,
                "created_at": datetime.now(),
                "plan_discount_percent": 10,
                "display_order": 3,
                "description": "باقة المؤسسات",
                "base_price": 8000,
            },
        ]

        plans = await get_active_subscription_plans()

        assert len(plans) == 3


@pytest.mark.asyncio
async def test_calculate_plan_price_success():
    """
    اختبار حساب سعر الباقة
    """
    with patch("app.repositories.subscription_plan_repo.get_subscription_plan_by_id") as mock_get:
        mock_get.return_value = {
            "id": 1,
            "code": "basic",
            "base_price": 3000,
            "plan_discount_percent": 10,
        }

        price = await calculate_plan_price(plan_id=1)

        assert price == 2700.0  # 3000 - 10%
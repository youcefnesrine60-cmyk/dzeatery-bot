# ==============================================
# 🧪 TEST ORDERS REPOSITORY
# ==============================================

import pytest
from unittest.mock import patch

from app.repositories.orders_repo import (
    create_order,
    get_order,
    get_restaurant_orders,
)


@pytest.mark.asyncio
async def test_create_order_success():
    """
    اختبار إنشاء طلب جديد بنجاح
    """
    with patch("app.repositories.orders_repo.insert_returning_id") as mock_insert:
        mock_insert.return_value = 1

        order_id = await create_order(
            restaurant_id=1,
            branch_id=None,
            table_id=None,
            employee_id=None,
            order_number="RST1-000001",
            order_type="dine_in",
            customer_name="علي",
            customer_phone="0555123456",
            delivery_address=None,
            customer_note=None,
            status="received",
            subtotal_amount=100,
            discount_amount=0,
            tax_amount=0,
            delivery_amount=0,
            total_amount=100,
        )

        assert order_id == 1
        mock_insert.assert_called_once()


@pytest.mark.asyncio
async def test_get_order_success():
    """
    اختبار جلب طلب معين
    """
    with patch("app.repositories.orders_repo.fetchrow") as mock_fetchrow:
        mock_fetchrow.return_value = {
            "id": 1,
            "restaurant_id": 1,
            "order_number": "RST1-000001",
            "status": "received",
            "total_amount": 100,
        }

        order = await get_order(order_id=1)

        assert order is not None
        assert order["id"] == 1
        assert order["order_number"] == "RST1-000001"


@pytest.mark.asyncio
async def test_get_restaurant_orders_success():
    """
    اختبار جلب جميع طلبات مطعم
    """
    with patch("app.repositories.orders_repo.fetch") as mock_fetch:
        mock_fetch.return_value = [
            {"id": 1, "order_number": "RST1-000001", "total_amount": 100},
            {"id": 2, "order_number": "RST1-000002", "total_amount": 150},
        ]

        orders = await get_restaurant_orders(restaurant_id=1)

        assert len(orders) == 2
        assert orders[0]["id"] == 1
        assert orders[1]["id"] == 2
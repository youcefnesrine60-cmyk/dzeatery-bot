# ==============================================
# 🧪 PYTEST CONFIGURATION
# إعدادات مشتركة لجميع الاختبارات
# ==============================================

import pytest
from unittest.mock import AsyncMock, patch

from app.core.db import init_db
from app.core.logger import logger


# ==============================================
# 🔧 ASYNCIO FIXTURE
# ==============================================

@pytest.fixture(scope="session")
def event_loop():
    """
    إنشاء event loop للاختبارات غير المتزامنة
    """
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==============================================
# 🗄️ DATABASE FIXTURE (Mock)
# ==============================================

@pytest.fixture
async def mock_db():
    """
    إنشاء اتصال وهمي بقاعدة البيانات
    """
    with patch("app.core.db.get_pool") as mock_pool:
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        
        # محاكاة تنفيذ الاستعلامات
        mock_cursor.fetchone.return_value = {"id": 1}
        mock_cursor.fetchall.return_value = []
        mock_cursor.execute.return_value = None
        
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_pool.return_value.connection.return_value.__aenter__.return_value = mock_conn
        
        yield mock_pool


# ==============================================
# 📦 DATA FACTORIES
# ==============================================

@pytest.fixture
def sample_owner_data():
    """
    بيانات مالك وهمية
    """
    return {
        "chat_id": 123456789,
        "full_name": "أحمد محمد",
        "phone": "0555123456",
        "email": "ahmed@example.com",
    }


@pytest.fixture
def sample_restaurant_data():
    """
    بيانات مطعم وهمية
    """
    return {
        "owner_id": 1,
        "name": "مطعم النخبة",
        "restaurant_type": "traditional",
        "phone": "0555123456",
        "wilaya": "الجزائر",
        "lat": 36.75,
        "lng": 3.06,
    }


@pytest.fixture
def sample_order_data():
    """
    بيانات طلب وهمية
    """
    return {
        "restaurant_id": 1,
        "branch_id": None,
        "table_id": None,
        "employee_id": None,
        "order_number": "RST1-000001",
        "order_type": "dine_in",
        "customer_name": "علي",
        "customer_phone": "0555123456",
        "delivery_address": None,
        "customer_note": "بدون بصل",
        "subtotal_amount": 100,
        "discount_amount": 0,
        "tax_amount": 0,
        "delivery_amount": 0,
        "total_amount": 100,
    }


@pytest.fixture
def sample_product_data():
    """
    بيانات منتج وهمية
    """
    return {
        "restaurant_id": 1,
        "category_id": 1,
        "name": "بيتزا مارجريتا",
        "description": "بيتزا كلاسيكية",
        "price": 800,
        "image_url": None,
        "sort_order": 0,
    }
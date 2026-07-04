# ==============================================
# 🧪 TEST MAIN
# ==============================================

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_app_creation():
    """
    اختبار إنشاء تطبيق FastAPI
    """
    from app.main import app

    assert app is not None
    assert app.title == "DZ Eatery Bot"
    assert app.version == "1.0.0"


@pytest.mark.asyncio
async def test_app_routes():
    """
    اختبار تسجيل المسارات في التطبيق
    """
    from app.main import app

    # التحقق من وجود المسارات
    routes = [route.path for route in app.routes]
    
    assert "/webhook" in routes
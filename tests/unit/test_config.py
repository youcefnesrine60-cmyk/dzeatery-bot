# ==============================================
# 🧪 TEST CONFIG
# ==============================================

import os
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_config_variables_exist():
    """
    اختبار وجود متغيرات البيئة
    """
    with patch.dict(os.environ, {
        "BOT_TOKEN": "test_bot_token",
        "DATABASE_URL": "postgresql://test:test@localhost/test",
        "OPENAI_API_KEY": "test_openai_key",
    }):
        import importlib
        import app.config
        importlib.reload(app.config)
        from app.config import BOT_TOKEN, DATABASE_URL, OPENAI_API_KEY

        assert BOT_TOKEN == "test_bot_token"
        assert DATABASE_URL == "postgresql://test:test@localhost/test"
        assert OPENAI_API_KEY == "test_openai_key"


@pytest.mark.asyncio
async def test_config_missing_variables():
    """
    اختبار التعامل مع المتغيرات المفقودة
    """
    # ✅ استخدام patch.object مع os.getenv مباشرة
    with patch.object(os, "getenv", return_value=None):
        import importlib
        import app.config
        importlib.reload(app.config)
        from app.config import BOT_TOKEN, DATABASE_URL, OPENAI_API_KEY

        assert BOT_TOKEN is None
        assert DATABASE_URL is None
        assert OPENAI_API_KEY is None
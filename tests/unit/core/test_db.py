# ==============================================
# 🧪 TEST DATABASE - الحل النهائي
# ==============================================

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.db import (
    init_db,
    get_pool,
    fetchrow,
    fetch,
    execute,
    insert_returning_id,
    transaction,
    close_db,
)


@pytest.mark.asyncio
async def test_init_db_success():
    """
    اختبار تهيئة قاعدة البيانات بنجاح
    """
    with patch("app.core.db.AsyncConnectionPool") as mock_pool:
        mock_pool.return_value.open = AsyncMock()
        
        await init_db()
        
        from app.core.db import db_pool
        assert db_pool is not None


@pytest.mark.asyncio
async def test_get_pool_success():
    """
    اختبار جلب pool قاعدة البيانات
    """
    with patch("app.core.db.init_db") as mock_init:
        mock_init.return_value = None
        
        from app.core.db import db_pool, get_pool
        db_pool = AsyncMock()
        
        pool = await get_pool()
        
        assert pool is not None


@pytest.mark.asyncio
async def test_fetchrow_success():
    """
    اختبار fetchrow
    """
    # ✅ استخدام MagicMock بدلاً من AsyncMock لمحاكاة async with بشكل صحيح
    # ✅ MagicMock يمكنه محاكاة async with بشكل أفضل
    
    # إنشاء Mock للـ cursor
    mock_cursor = MagicMock()
    mock_cursor.execute = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value={"id": 1, "name": "test"})
    
    # جعل cursor مدير سياق غير متزامن
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=None)
    
    # إنشاء Mock للـ connection
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # جعل connection مدير سياق غير متزامن
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)
    
    # إنشاء Mock للـ pool
    mock_pool = MagicMock()
    mock_pool.connection.return_value = mock_conn
    
    with patch("app.core.db.get_pool", return_value=mock_pool):
        result = await fetchrow("SELECT * FROM test WHERE id = %s", 1)
        
        assert result is not None
        assert result["id"] == 1
        assert result["name"] == "test"
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchone.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_success():
    """
    اختبار fetch
    """
    mock_cursor = MagicMock()
    mock_cursor.execute = AsyncMock()
    mock_cursor.fetchall = AsyncMock(return_value=[
        {"id": 1, "name": "test1"},
        {"id": 2, "name": "test2"},
    ])
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=None)
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)
    
    mock_pool = MagicMock()
    mock_pool.connection.return_value = mock_conn
    
    with patch("app.core.db.get_pool", return_value=mock_pool):
        result = await fetch("SELECT * FROM test")
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2


@pytest.mark.asyncio
async def test_execute_success():
    """
    اختبار execute
    """
    mock_cursor = MagicMock()
    mock_cursor.execute = AsyncMock()
    mock_cursor.statusmessage = "INSERT 0 1"
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=None)
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)
    
    mock_pool = MagicMock()
    mock_pool.connection.return_value = mock_conn
    
    with patch("app.core.db.get_pool", return_value=mock_pool):
        result = await execute("INSERT INTO test (name) VALUES (%s)", "test")
        
        assert result == "INSERT 0 1"


@pytest.mark.asyncio
async def test_insert_returning_id_success():
    """
    اختبار insert_returning_id
    """
    mock_cursor = MagicMock()
    mock_cursor.execute = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=(1,))
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=None)
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)
    
    mock_pool = MagicMock()
    mock_pool.connection.return_value = mock_conn
    
    with patch("app.core.db.get_pool", return_value=mock_pool):
        result = await insert_returning_id(
            "INSERT INTO test (name) VALUES (%s) RETURNING id",
            "test"
        )
        
        assert result == 1


@pytest.mark.asyncio
async def test_transaction_success():
    """
    اختبار transaction context manager
    """
    # محاكاة transaction
    mock_conn = MagicMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)
    mock_conn.transaction.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.transaction.return_value.__aexit__ = AsyncMock(return_value=None)
    
    mock_pool = MagicMock()
    mock_pool.connection.return_value = mock_conn
    
    with patch("app.core.db.get_pool", return_value=mock_pool):
        async with transaction() as conn:
            assert conn is not None


@pytest.mark.asyncio
async def test_close_db_success():
    """
    اختبار close_db
    """
    with patch("app.core.db.db_pool", AsyncMock()) as mock_pool:
        mock_pool.close = AsyncMock()
        
        from app.core.db import close_db
        await close_db()
        
        mock_pool.close.assert_called_once()
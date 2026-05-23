import httpx

from app.core.logger import (
    logger
)

# ============================================
# 🌐 HTTP CLIENT
# ============================================

client = httpx.AsyncClient(

    timeout=httpx.Timeout(20.0),

    follow_redirects=True,

    limits=httpx.Limits(

        max_keepalive_connections=20,

        max_connections=100
    )
)

# ============================================
# ❌ CLOSE HTTP CLIENT
# ============================================

async def close_http_client() -> None:

    await client.aclose()

    logger.info(
        "telegram_http_client_closed"
    )
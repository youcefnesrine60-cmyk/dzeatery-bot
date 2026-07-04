import httpx

from app.core.logger import logger

# ============================================
# 🌐 SHARED HTTP CLIENT
# ============================================

client: httpx.AsyncClient = httpx.AsyncClient(
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

    logger.info(
        "closing_telegram_http_client"
    )

    await client.aclose()

    logger.info(
        "telegram_http_client_closed"
    )
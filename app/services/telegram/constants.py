from app.config import BOT_TOKEN

# ============================================
# 🌐 TELEGRAM API CONSTANTS
# ============================================

BASE_URL: str = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
)

PARSE_MODE: str = "HTML"

MAX_RETRIES: int = 3
from app.config import (
    BOT_TOKEN
)

# ============================================
# 🌐 CONSTANTS
# ============================================

BASE_URL = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
)

PARSE_MODE = "HTML"

MAX_RETRIES = 3
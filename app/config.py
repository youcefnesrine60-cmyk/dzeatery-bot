import os
from dotenv import load_dotenv

# ============ ENV loader =============

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
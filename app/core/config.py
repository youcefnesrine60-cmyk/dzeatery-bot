# ==============================================
# ⚙️ APPLICATION CONFIGURATION
# إدارة إعدادات التطبيق من ملف .env
# ==============================================

from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# ==============================================
# 🌍 LOAD ENVIRONMENT VARIABLES
# ==============================================

load_dotenv()


# ==============================================
# ⚙️ SETTINGS
# ==============================================

class Settings(BaseSettings):
    """
    إعدادات التطبيق

    يتم قراءة القيم من ملف .env
    """

    # ==========================================
    # 🌐 GENERAL
    # ==========================================

    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "MoulAI"
    APP_VERSION: str = "1.0.0"
    APP_URL: str = "https://onrender.com"

    # ==========================================
    # 🐘 DATABASE
    # ==========================================

    DATABASE_URL: str  # لـ SQLAlchemy (مع +asyncpg)
    DATABASE_SYNC_URL: Optional[str] = None  # لـ Psycopg3 (بدون +asyncpg)

    # ==========================================
    # 🔴 REDIS
    # ==========================================

    REDIS_URL: str

    # ==========================================
    # 🤖 TELEGRAM
    # ==========================================

    BOT_TOKEN: str
    WEBHOOK_URL: str
    WEBHOOK_PATH: str = "/webhook"

    # ==========================================
    # 🤖 AI
    # ==========================================

    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o-mini"

    # ==========================================
    # 🔐 SECURITY
    # ==========================================

    SECRET_KEY: str

    # ==========================================
    # 🌐 CORS
    # ==========================================

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # ==========================================
    # 📊 PERFORMANCE & RATE LIMITING
    # ==========================================

    # 🟢 إعدادات Pool المحسّنة
    DB_ECHO: bool = False  # سيتم ضبطها تلقائياً حسب APP_ENV
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 20  # ✅ قيمة متوسطة (بدلاً من 40)
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 3600  # ✅ إعادة التدوير كل ساعة

    REDIS_POOL_SIZE: int = 10
    REDIS_POOL_TIMEOUT: int = 5

    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # ==========================================
    # 📝 LOGGING
    # ==========================================

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "logs/app.log"

    # ==========================================
    # 🏪 SUBSCRIPTION
    # ==========================================

    DEFAULT_SUBSCRIPTION_PLAN: str = "basic"
    TRIAL_PERIOD_DAYS: int = 14
    MAX_RESTAURANTS_PER_OWNER: int = 10
    TENANT_ISOLATION_LEVEL: str = "strict"

    # ==========================================
    # 🛠️ HELPER PROPERTIES
    # ==========================================

    @property
    def IS_DEVELOPMENT(self) -> bool:
        """التحقق مما إذا كانت البيئة هي Development"""
        return self.APP_ENV == "development"

    @property
    def IS_PRODUCTION(self) -> bool:
        """التحقق مما إذا كانت البيئة هي Production"""
        return self.APP_ENV == "production"

    @property
    def IS_TESTING(self) -> bool:
        """التحقق مما إذا كانت البيئة هي Testing"""
        return self.APP_ENV == "testing"

    @property
    def DB_ECHO_ENABLED(self) -> bool:
        """
        تحديد ما إذا كان سيتم طباعة استعلامات SQL
        
        يتم تفعيلها تلقائياً في بيئة التطوير
        """
        return self.IS_DEVELOPMENT and self.DEBUG

    # ==========================================
    # 🔧 MODEL CONFIG
    # ==========================================

    class Config:
        """إعدادات Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # تجاهل أي متغيرات زائدة


# ==============================================
# 🌍 GLOBAL INSTANCE
# ==============================================

# إنشاء كائن الإعدادات لاستخدامه في كل مكان
settings = Settings()

# ==============================================
# 🔄 APPLY DYNAMIC DB_ECHO
# ==============================================

# ضبط DB_ECHO تلقائياً حسب البيئة
settings.DB_ECHO = settings.DB_ECHO_ENABLED
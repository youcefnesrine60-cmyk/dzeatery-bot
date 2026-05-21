#=======================================
# decision engine محرك اتخاذ القرار
# هذا أهم ملف. هو الذي يقرر
# allow   السماح
# deny    الرفض
# ban     الحظر
# cooldown   فترة التهدئة
# flag  رفع راية
#========================================

from app.core.security.anti_spam import (
    AntiSpam
)

from app.core.security.anti_bot import (
    AntiBot
)

from app.core.security.abuse_detector import (
    AbuseDetector
)

from app.core.security.fraud_detector import (
    FraudDetector
)

from app.core.security.ban_manager import (
    BanManager
)

from app.core.security.captcha_manager import (
    CaptchaManager
)

from app.handlers.captcha_handler import (
    send_captcha
)

from app.core.logger import logger


# ==============================================
# 🛡️ RISK ENGINE
# ==============================================

class RiskEngine:

    @staticmethod
    async def analyze(
        chat_id: int,
        text: str
    ) -> bool:

        # ======================================
        # TEMPORARY:
        # Security system disabled
        # ======================================

        return True
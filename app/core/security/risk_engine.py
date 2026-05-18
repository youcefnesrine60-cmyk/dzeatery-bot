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


# ==========================================
# 🛡️ RISK ENGINE
# ==========================================

class RiskEngine:

    @classmethod
    async def analyze(

        cls: type,

        chat_id: int
    ) -> bool:

        # ======================================
        # 🚫 BANNED USERS
        # ======================================

        banned = await BanManager.is_banned(
            chat_id
        )

        if banned:

            logger.warning(

                "banned_user_blocked",

                extra={
                    "chat_id": chat_id
                }
            )

            return False

        # ======================================
        # 🤖 CAPTCHA REQUIRED
        # ======================================

        captcha = await CaptchaManager.is_required(
            chat_id
        )

        if captcha:

            await send_captcha(chat_id)

            return False

        # ======================================
        # 🚫 SPAM DETECTION
        # ======================================

        spam_ok = await AntiSpam.check(
            chat_id
        )

        if not spam_ok:

            logger.warning(

                "spam_detected",

                extra={
                    "chat_id": chat_id
                }
            )

            await AbuseDetector.flag(
                chat_id
            )

            await FraudDetector.flag(

                chat_id,

                severity=5
            )

            return False

        # ======================================
        # 🤖 BOT DETECTION
        # ======================================

        bot_ok = await AntiBot.check(
            chat_id
        )

        if not bot_ok:

            logger.warning(

                "bot_detected",

                extra={
                    "chat_id": chat_id
                }
            )

            await AbuseDetector.flag(
                chat_id
            )

            await FraudDetector.flag(

                chat_id,

                severity=10
            )

            return False

        # ======================================
        # 🚫 ABUSE DETECTION
        # ======================================

        abusive = await AbuseDetector.is_abusive(
            chat_id
        )

        if abusive:

            logger.warning(

                "abusive_user_detected",

                extra={
                    "chat_id": chat_id
                }
            )

            await BanManager.ban(

                chat_id,

                ttl=86400
            )

            return False

        # ======================================
        # ✅ SAFE
        # ======================================

        return True
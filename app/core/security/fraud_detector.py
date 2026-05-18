#=====================
# كشف الاحتيال
#=====================

from app.core.security.fraud_storage import (
    FraudStorage
)

from app.core.security.fraud_score import (
    FraudScore
)

from app.core.security.ban_manager import (
    BanManager
)

from app.core.security.captcha_manager import (
    CaptchaManager
)

class FraudDetector:

    @classmethod
    async def flag(

        cls: type,

        chat_id: int,

        severity: int
    ) -> None:

        await FraudStorage.add_score(

            chat_id,

            severity
        )

        total = await FraudStorage.get_score(
            chat_id
        )

        # ======================================
        # 🚫 CAPTCHA
        # ======================================

        if total >= FraudScore.MEDIUM:

            await CaptchaManager.require(
                chat_id
            )

        # ======================================
        # 🚫 TEMP BAN
        # ======================================

        if total >= FraudScore.HIGH:

            await BanManager.ban(

                chat_id,

                ttl=3600
            )

        # ======================================
        # 🚫 PERMANENT-LIKE BAN
        # ======================================

        if total >= FraudScore.CRITICAL:

            await BanManager.ban(

                chat_id,

                ttl=86400 * 30
            )
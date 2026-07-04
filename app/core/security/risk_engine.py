# ==============================================
# 🛡️ RISK ENGINE
# ==============================================
from app.core.logger import logger

class RiskEngine:

    @staticmethod
    async def analyze(
        chat_id: int,
        text: str | None = None
    ) -> bool:

        # ======================================
        # TEMPORARY:
        # Security disabled
        # ======================================

        logger.info(
            "risk_analysis_completed",
            extra={
                "chat_id": chat_id
            }
        )

        return True
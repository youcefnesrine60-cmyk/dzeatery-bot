# ==============================================
# 🆔 TRACE HELPER
# ==============================================

import uuid

from app.core.logger import logger

# ==============================================
# 🆔 TRACE
# ==============================================

class Trace:

    @staticmethod
    def generate() -> str:

        trace_id = str(
            uuid.uuid4()
        )

        logger.info(
            "trace_generated",
            extra={
                "trace_id": trace_id,
            },
        )

        return trace_id
import logging
import sys

from pythonjsonlogger import jsonlogger


# ==========================================
# SAFE JSON FORMATTER
# ==========================================

class SafeJsonFormatter(
    jsonlogger.JsonFormatter
):

    def add_fields(

        self,

        log_record,

        record,

        message_dict
    ):

        super().add_fields(

            log_record,

            record,

            message_dict
        )

        # ==================================
        # SAFE DEFAULTS
        # ==================================

        log_record.setdefault(

            "chat_id",

            "-"
        )

        log_record.setdefault(

            "event",

            "-"
        )

        log_record.setdefault(

            "order_id",

            "-"
        )


# ==========================================
# LOGGER
# ==========================================

logger = logging.getLogger(
    "DZ_EATERY"
)

logger.setLevel(logging.INFO)

handler = logging.StreamHandler(
    sys.stdout
)

formatter = SafeJsonFormatter(

    "%(asctime)s "
    "%(levelname)s "
    "%(event)s "
    "%(chat_id)s "
    "%(order_id)s "
    "%(message)s"
)

handler.setFormatter(formatter)

logger.addHandler(handler)

logger.propagate = False
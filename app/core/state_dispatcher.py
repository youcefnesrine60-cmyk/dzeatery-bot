# ==============================================
# 🧠 STATE DISPATCHER
# ==============================================

from app.core.logger import logger
from app.handlers.owner_handler import handle_owner_state
from app.handlers.customer_handler import handle_customer_state

class StateDispatcher:

    @classmethod
    async def dispatch(
        cls,
        *,
        chat_id: int,
        text: str,
        state: dict,
    ) -> None:
        """
        توزيع الحالة إلى المعالج المناسب
        
        Args:
            chat_id: معرف المستخدم
            text: النص المرسل
            state: حالة المستخدم الحالية
        """
        flow = state.get("flow")

        # ==========================================
        # OWNER FLOW
        # ==========================================

        if flow == "owner":
            return await handle_owner_state(
                chat_id=chat_id,
                text=text,
                state=state,
            )

        # ==========================================
        # CUSTOMER FLOW
        # ==========================================

        elif flow == "customer":
            return await handle_customer_state(
                chat_id=chat_id,
                text=text,
                state=state,
            )

        # ==========================================
        # UNKNOWN FLOW
        # ==========================================

        logger.warning(
            "unknown_flow_state",
            extra={
                "chat_id": chat_id,
                "flow": flow,
            },
        )

        return None
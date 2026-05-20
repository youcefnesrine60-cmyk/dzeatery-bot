from app.handlers.owner_handler import (
    handle_owner_state
)

from app.handlers.customer_handler import (
    handle_customer_state
)

class StateDispatcher:

    @classmethod
    async def dispatch(

        cls: 'StateDispatcher',

        chat_id: int,

        text: str,

        state: dict
    ) -> any:

        flow = state.get("flow")

        # ==========================================
        # OWNER FLOW
        # ==========================================


        if flow == "owner":

            return await handle_owner_state(

                chat_id,

                text,

                state
            )

        # ==========================================
        # CUSTOMER FLOW
        # مؤقتًا غير مفعل
        # ==========================================

        #elif flow == "customer":

            return await handle_customer_state(

                chat_id,

                text,

                state
            )#.customer flow is currently disabled, so we return None for now
        return None
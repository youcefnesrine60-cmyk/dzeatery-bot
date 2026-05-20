from app.states.customer_states import (
    CustomerStates
)


from app.core.logger import (
    logger
)

# ==============================================
# 🧠 CUSTOMER STATE ROUTER
# ==============================================

async def handle_customer_state(

    chat_id: int,

    text: str,

    state: dict

) -> None:

    step = state["step"]

    if step == CustomerStates.RESTAURANT:

        logger.info(
            "Handling restaurant step for chat_id {chat_id} with text: {text}",
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        #await handle_restaurant_step(
            #chat_id,
            #text,
            #state
        #)

    elif step == CustomerStates.PRODUCT:

        logger.info(
            "Handling product step for chat_id {chat_id} with text: {text}",
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        #await handle_product_step(
            #chat_id,
            #text,
            #state
        #)

    elif step == CustomerStates.CART:

        logger.info(
            "Handling cart step for chat_id {chat_id} with text: {text}",
            extra={
                "chat_id": chat_id,
                "text": text
            }
        )

        #await handle_cart_step(
            #chat_id,
            #text,
            #state
        #)
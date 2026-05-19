from app.core.redis_client import r
from app.core.logger import (
    logger
)
import json

def get_state(chat_id: int) -> dict | None:
    data = r.get(f"user:{chat_id}")
    if data:
        logger.info("Retrieving state for user {chat_id}", extra={"chat_id": chat_id})
        return json.loads(data)
    logger.warning("No state found for user {chat_id}", extra={"chat_id": chat_id})
    return None

def set_state(chat_id: int, state: dict) -> None:
    logger.info(
        "Setting state for user {chat_id}: {state}", 
        extra={
            "chat_id": chat_id, 
            "state": state
        }
    )
    r.set(f"user:{chat_id}", json.dumps(state))

def delete_state(chat_id: int) -> None:
    logger.info(
        "Deleting state for user {chat_id}", 
        extra={
            "chat_id": chat_id
        }
    )
    r.delete(f"user:{chat_id}")
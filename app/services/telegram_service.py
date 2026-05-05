import requests
from core.config import BOT_TOKEN
from core.logger import logger


BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ================== CORE REQUEST ==================
def _post(method, data):
    try:
        res = requests.post(f"{BASE_URL}/{method}", json=data).json()

        if not res.get("ok"):
            logger.error(f"{method} failed: {res}")

        return res

    except Exception as e:
        logger.exception(f"{method} exception")
        return None

# ================== SEND MESSAGE ==================
def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return _post("sendMessage", data)


# ================== EDIT MESSAGE ==================
def edit_message(chat_id, message_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return _post("editMessageText", data)


# ================== DELETE MESSAGE ==================
def delete_message(chat_id, message_id):
    return _post("deleteMessage", {
        "chat_id": chat_id,
        "message_id": message_id
    })


# ================== ANSWER CALLBACK ==================
def answer_callback(callback_id):
    return _post("answerCallbackQuery", {
        "callback_query_id": callback_id
    })
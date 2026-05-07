import requests
from app.config import BOT_TOKEN
from app.logger import logger

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def _post(method, data):
    try:
        res = requests.post(f"{BASE_URL}/{method}", json=data).json()
        if not res.get("ok"):
            logger.error(f"{method} error: {res}")
        return res
    except Exception as e:
        logger.error(f"Telegram exception: {e}")

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return _post("sendMessage", data)

def edit_message(chat_id, message_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return _post("editMessageText", data)

def delete_message(chat_id, message_id):
    return _post("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id):
    return _post("answerCallbackQuery", {"callback_query_id": callback_id})

def set_webhook(url):
    return _post("setWebhook", {"url": url})
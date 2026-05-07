from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.controllers.bot_controller import handle_update

import requests
import os

app = FastAPI()

# ✅ mount خارج startup
app.mount("/static", StaticFiles(directory="app/webapp"), name="static")

# ================= WEBHOOK =================
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    handle_update(data)
    return {"ok": True}

# ================= SET WEBHOOK =================
@app.on_event("startup")
def set_webhook():
    url = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/setWebhook"
    requests.post(url, json={"url": os.getenv("WEBHOOK_URL")})

# ================= WEBAPP PAGE =================
@app.get("/webapp", response_class=HTMLResponse)
def map_page():
    with open("app/webapp/map.html", "r", encoding="utf-8") as f:
        return f.read()
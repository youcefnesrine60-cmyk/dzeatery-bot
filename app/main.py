from fastapi import FastAPI, Request
from controllers.bot_controller import handle_update

app = FastAPI()

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    handle_update(data)
    return {"ok": True}
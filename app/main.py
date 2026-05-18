from fastapi import FastAPI

from app.api.webhook import router


app = FastAPI(

    title="DZ Eatery Bot",

    version="1.0.0"
)

app.include_router(router)
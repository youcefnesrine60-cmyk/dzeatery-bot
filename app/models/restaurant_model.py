# ==============================================
# 🍔 RESTAURANT SCHEMAS
# ==============================================

from pydantic import BaseModel

# ==============================================
# ➕ CREATE RESTAURANT
# ==============================================

class RestaurantCreate(
    BaseModel,
):

    name: str

    owner: str

    type: str

    phone: str

    wilaya: str

    lat: float

    lng: float

    chat_id: int
from pydantic import BaseModel


class RestaurantCreate(BaseModel):

    name: str

    owner: str

    type: str

    phone: str

    wilaya: str

    lat: float

    lng: float

    chat_id: int
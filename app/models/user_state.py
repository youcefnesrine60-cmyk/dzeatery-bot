from pydantic import BaseModel
from typing import Optional


class UserState(BaseModel):

    step: str

    history: list[str] = []

    owner: Optional[str] = None

    restaurant: Optional[str] = None

    wilaya: Optional[str] = None

    lat: Optional[float] = None

    lng: Optional[float] = None

    type: Optional[str] = None

    phone: Optional[str] = None
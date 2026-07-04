# ==============================================
# 👤 USER STATE SCHEMA
# ==============================================

from typing import Optional

from pydantic import BaseModel, Field

# ==============================================
# 🧠 USER STATE
# ==============================================

class UserState(
    BaseModel,
):

    step: str

    history: list[str] = Field(
        default_factory=list,
    )

    owner: Optional[str] = None

    restaurant: Optional[str] = None

    wilaya: Optional[str] = None

    lat: Optional[float] = None

    lng: Optional[float] = None

    type: Optional[str] = None

    phone: Optional[str] = None
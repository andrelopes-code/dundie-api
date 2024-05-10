from datetime import datetime
from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    image: str
    description: str | None = None
    price: int
    created_at: datetime

from datetime import datetime
from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    image: str
    description: str | None = None
    price: int
    created_at: datetime


class ProductRequest(BaseModel):
    name: str
    image: str
    description: str | None = None
    price: int


class ProductUpdateRequest(BaseModel):
    id: int
    name: str | None = None
    image: str | None = None
    description: str | None = None
    price: int | None = None

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from dundie.utils.utils import get_utcnow


class Products(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(max_length=255, nullable=False)
    image: str = Field(nullable=False)
    price: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=get_utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=get_utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": get_utcnow}
    )


class Orders(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    product_id: int = Field(foreign_key="products.id", nullable=False)
    product: str = Field(max_length=255, nullable=False)
    product_img: str = Field(nullable=False)
    name: str = Field(max_length=255, nullable=False)
    status: str = Field(default="pending", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=get_utcnow,
        nullable=False,
        index=True
    )

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from dundie.utils.utils import get_utcnow


class Products(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    description: str = Field(max_length=255, nullable=False)
    image: str = Field(nullable=False)
    price: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=get_utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=get_utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": get_utcnow}
    )

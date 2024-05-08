from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from dundie.utils.utils import get_utcnow


class Feedbacks(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, nullable=False)
    feedback: str = Field(max_length=255, nullable=False)
    status: str = Field(default="pending", nullable=False)
    created_at: datetime = Field(default_factory=get_utcnow, nullable=False)

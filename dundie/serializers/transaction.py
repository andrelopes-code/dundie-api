from datetime import datetime

from pydantic import BaseModel

from .user import UserResponse


class RankingResponse(BaseModel):
    id: int
    name: str
    username: str
    avatar: str | None
    points: int


class RecentTransactionsResponse(BaseModel):
    from_id: int
    to_id: int
    from_user: UserResponse
    to_user: UserResponse
    points: int
    date: datetime

from pydantic import BaseModel


class RankingResponse(BaseModel):
    id: int
    name: str
    username: str
    avatar: str | None
    points: int

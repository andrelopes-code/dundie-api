from datetime import datetime
from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    feedback: str
    email: str


class FeedbackResponse(BaseModel):
    id: int
    email: str
    name: str
    feedback: str
    status: str
    created_at: datetime

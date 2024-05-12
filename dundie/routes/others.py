from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select
from dundie.auth.functions import AuthenticatedUser
from dundie.db import ActiveSession
from dundie.models import Feedbacks, User
from dundie.serializers.others import (
    FeedbackRequest,
    FeedbackResponse,
)

router = APIRouter()


@router.get(
    '/feedback/all',
    response_model=Page[FeedbackResponse],
)
async def list_feedbacks(
    session: Session = ActiveSession,
    params: Params = Depends(),
):
    """Returns all feedbacks"""
    query = select(Feedbacks).order_by(Feedbacks.created_at.desc())
    try:
        # Paginates the user list response
        return paginate(query=query, params=params, session=session)
    except Exception as e:
        print(e)

    raise HTTPException(404, 'failed to return feedbacks')


@router.post(
    '/feedback/send',
    response_model=FeedbackResponse,
)
async def send_feedback(
    feedback_data: FeedbackRequest,
    user: User = AuthenticatedUser,
    session: Session = ActiveSession,
    params: Params = Depends(),
):
    """Send feedback"""

    new_feedback = Feedbacks(
        email=feedback_data.email,
        feedback=feedback_data.feedback,
        name=user.name,
    )

    session.add(new_feedback)
    try:
        session.commit()
        session.refresh(new_feedback)
    except Exception as e:
        print(e)

    return new_feedback

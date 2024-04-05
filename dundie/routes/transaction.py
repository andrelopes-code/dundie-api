from fastapi import APIRouter
from sqlmodel import Session
from dundie.db import ActiveSession
from dundie.auth.functions import AuthenticatedUser
from dundie.models import User
from dundie.controllers.transaction import check_and_transfer_points
from dundie.auth.functions import get_user

router = APIRouter()


@router.post(
    '/{username}',
    summary='Transfer poinst from an user to another user',
)
async def transfer_points_to_another_user(
    username: str,
    points: int,
    auth_user: User = AuthenticatedUser,
    session: Session = ActiveSession
):

    from_user = get_user(
        username=auth_user.username,
        session=session
    )

    transaction = check_and_transfer_points(
        from_user=from_user,
        points=points,
        session=session,
        username=username
    )

    return transaction

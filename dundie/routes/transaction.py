from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from dundie.auth.functions import AuthenticatedUser, get_user
from dundie.controllers.transaction import check_and_transfer_points
from dundie.db import ActiveSession
from dundie.models import User, Balance

router = APIRouter()


@router.post(
    '/transaction/{username}',
    summary='Transfer poinst from an user to another user',
)
async def transfer_points_to_another_user(
    username: str,
    points: int,
    auth_user: User = AuthenticatedUser,
    session: Session = ActiveSession,
):
    """
    A function to transfer points from one user to another.

    Args:
        - username (str): The username of the user transferring the points.
        - points (int): The amount of points to be transferred.
        - auth_user (User): The authenticated user performing the transfer.
        - session (Session): The active session for the transfer.

    Returns:
        transaction: The transaction object representing the points transfer.
    """
    if auth_user.username == username:
        raise HTTPException(400, 'It is not possible to transfer to yourself')

    from_user = get_user(username=auth_user.username, session=session)

    transaction = check_and_transfer_points(
        from_user=from_user,
        points=points,
        session=session,
        username=username
    )

    return transaction


@router.get(
    '/ranking',
    summary='get the points ranking',
    dependencies=[AuthenticatedUser]
)
async def get_points_ranking(*, session: Session = ActiveSession):
    """
    A function to get the points ranking from the database.

    Parameters:
        - session (Session): The database session to use for the query.

    Returns:
        list: A list of dictionaries containing user information and their
        points ranking.
    """

    stmt = select(User).join(Balance).order_by(Balance.value.desc()).limit(10)
    result = session.exec(stmt).all()

    ranking = [user.model_dump() for user in result]

    for rank_idx, user in enumerate(result):
        ranking[rank_idx].update({'points': user.balance})

    return ranking

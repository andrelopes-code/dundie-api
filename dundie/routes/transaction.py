from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import or_
from sqlmodel import Session, select

from dundie.auth.functions import AuthenticatedUser, get_user
from dundie.controllers.transaction import check_and_transfer_points
from dundie.db import ActiveSession
from dundie.models import Balance, Transaction, User
from dundie.serializers.transaction import (
    RankingResponse,
    RecentTransactionsResponse,
    UserTransactionsResponse,
)


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
        from_user=from_user, points=points, session=session, username=username
    )

    return transaction


@router.get(
    '/ranking',
    summary='get the points ranking',
    dependencies=[AuthenticatedUser],
    response_model=List[RankingResponse],
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


@router.get(
    '/transaction/recent',
    response_model=List[RecentTransactionsResponse],
    dependencies=[AuthenticatedUser],
)
async def get_recent_transactions(session: Session = ActiveSession):
    """
    A function that returns the 5 most recent transactions in the database
    """

    stmt = select(Transaction).order_by(Transaction.date.desc()).limit(5)
    transactions = session.exec(stmt).all()

    # ! I know this is not the best way to do this
    trans_dict = [
        {
            "from_id": t.from_id,
            "to_id": t.user_id,
            "from_user": t.from_user,
            "to_user": t.user,
            "points": t.value,
            "date": t.date,
        }
        for t in transactions
    ]

    return trans_dict


@router.get(
    '/transaction/list',
    response_model=List[UserTransactionsResponse],
)
async def get_user_transactions(
    username: str = None,
    *,
    user: User = AuthenticatedUser,
    session: Session = ActiveSession,
):
    """
    A function that returns all the authenticated user transactions if no
    username is passed. If a username is passed, it returns all the
    transactions of the user with the specified username. The transactions
    are sorted by date in descending order.
    """
    # TODO: add pagination to this endpoint to avoid loading all data

    # Defines the user ID to be used in the query
    if username:
        uid = get_user(username=username, session=session).id
    else:
        uid = user.id

    # Selects the transactions the user is involved in
    stmt = (
        select(Transaction)
        .where(or_(Transaction.user_id == uid, Transaction.from_id == uid))
        .order_by(Transaction.date.desc())
    )
    transactions = session.exec(stmt).all()

    # ! I know this is not the best way to do this
    # TODO: refactor this
    trans_dict = [
        {
            "id": t.id,
            "from_id": t.from_id,
            "to_id": t.user_id,
            "from_user": t.from_user,
            "to_user": t.user,
            "points": t.value,
            "date": t.date,
        }
        for t in transactions
    ]

    return trans_dict

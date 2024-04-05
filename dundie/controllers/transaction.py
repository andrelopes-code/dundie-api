from fastapi import HTTPException
from sqlmodel import Session, select

from dundie.auth.functions import get_user
from dundie.db import engine
from dundie.exc import SystemDefaultUserNotFound
from dundie.models import Balance, Transaction, User


def make_transaction(
    to_user: User,
    from_user: User,
    points: int,
    session: Session,
):

    transaction = Transaction(
        user_id=to_user.id, from_id=from_user.id, value=points
    )

    # Gets the 'from_user' Balance object
    stmt = select(Balance).where(Balance.user_id == from_user.id)
    from_user_balance: Balance = session.exec(stmt).first()

    # Gets the 'to_user' Balance object
    stmt = select(Balance).where(Balance.user_id == to_user.id)
    to_user_balance: Balance = session.exec(stmt).first()

    # Updates users points
    from_user_balance.value -= points if not from_user.superuser else 0
    to_user_balance.value += points

    # COMMIT THE BALANCES
    try:
        session.add(transaction)
        session.add(to_user_balance)
        session.add(from_user_balance)
        session.commit()
        session.refresh(transaction)
    except Exception:
        raise HTTPException(
            500, 'An error occurred while performing the transfer'
        )

    return {
        'from': from_user.username,
        'to': to_user.username,
        'value': points,
        'date': transaction.date,
    }


def check_and_transfer_points(
    username: str,
    points: int,
    from_user: User | None = None,
    session: Session | None = None,
):

    # Checks whether the transaction can be carried out
    if from_user and from_user.balance < points and not from_user.superuser:
        raise HTTPException(403, 'Insufficient funds')

    # Gets the reiceiving user
    to_user = get_user(username)
    if not to_user:
        raise HTTPException(404, 'User not found, impossible to transfer')

    # If not from_user, use system 'PointsDeliveryMan' user to send points
    if not from_user:
        from_user = get_user('pointsdeliveryman')
        if not from_user:
            raise SystemDefaultUserNotFound()

    if session:
        transaction = make_transaction(
            from_user=from_user,
            to_user=to_user,
            points=points,
            session=session,
        )
    else:
        with Session(engine) as session:
            transaction = make_transaction(
                from_user=from_user,
                to_user=to_user,
                points=points,
                session=session,
            )

    return transaction

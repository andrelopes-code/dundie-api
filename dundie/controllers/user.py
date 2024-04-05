from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from dundie.models import Balance, User


def create_user_and_balance(user_data, session: Session) -> User:
    db_user = User.model_validate(user_data)
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)

    except IntegrityError:
        session.rollback()
        raise HTTPException(500, 'Database IntegrityError')

    user_balance: Balance = Balance(user_id=db_user.id, value=0)
    session.add(user_balance)
    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(500, 'Database IntegrityError')

    return db_user

from random import choice, randint
from time import time

from sqlmodel import Session, select

from dundie.controllers.transaction import make_transaction
from dundie.models import User, Transaction
from dundie.db import engine
from .random_posts import get_random_date

PRIVATE = ['pointsdeliveryman', 'admin']

def get_user(username, session):
    stmt = select(User).where(User.username == username)
    return session.exec(stmt).first()

def create_random_transactions(quantity=30):
    count = 0

    with Session(engine) as session:

        stmt = select(User.username).where(User.is_active == True)
        usernames = session.exec(stmt).all()

        while count < quantity:

            to_user = choice(usernames)
            from_user = choice(usernames)
            if from_user == to_user:
                continue
            if from_user in PRIVATE or to_user in PRIVATE:
                continue
            
            to_user = get_user(to_user, session)
            from_user = get_user(from_user, session)
            value = randint(50, 800)
            
            try:
                make_transaction(
                    to_user=to_user,
                    from_user=from_user,
                    points=value,
                    session=session,
                )
                count += 1
            except Exception:
                raise ValueError("ERROR")

        # Update all transactions dates to be random
        all_transactions = session.exec(select(Transaction)).all()
        for t in all_transactions:
            t.date = get_random_date()
            session.add(t)
        
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            return {"detail": str(e)}

    return {"status": "ok"}
from random import choice, randint
from time import time

from sqlmodel import Session, select

from dundie.controllers.transaction import make_transaction
from dundie.models import User


def create_target_transactions(session: Session):
    st = time()
    count = 0

    usernames = [
        'livia',
        'frank',
        'grace',
        'henry',
        'david',
        'samuel',
        'jack',
        'taylor'
    ]

    while count < 30:

        target = 'andrelps'

        if count % 2 == 0:
            fu_username = target
            tu_username = choice(usernames)
        else:
            tu_username = target
            fu_username = choice(usernames)

        if fu_username == tu_username:
            continue

        fu = session.exec(
            select(User).where(User.username == fu_username)
        ).first()
        tu = session.exec(
            select(User).where(User.username == tu_username)
        ).first()

        if not (fu and tu):
            print("NAO TEM USERS")

        print(tu_username, fu_username)

        print(
            f"""
            for user id: {fu.id} - {fu_username}
            to user id: {tu.id} - {tu_username}
            """
        )

        try:
            make_transaction(
                to_user=tu,
                from_user=fu,
                points=randint(100, 2500),
                session=session,
            )
            count += 1
        except Exception:
            raise ValueError("ERRO DE NOVO")

    print(time() - st)

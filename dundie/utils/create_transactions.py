from random import choice, randint
from time import time

from sqlmodel import Session, select

from dundie.controllers.transaction import make_transaction
from dundie.models import User


def create_test_transactions(session: Session):
    st = time()
    users = [
        {
            'name': 'David',
            'email': 'david@example.com',
            'password': 'Dav1dPass!',
            'dept': 'Finance',
            'currency': 'USD',
            'username': 'david_1234',
        },
        {
            'name': 'Emily',
            'email': 'emily@example.com',
            'password': 'EmiLyp@ss',
            'dept': 'HR',
            'currency': 'USD',
            'username': 'emily_5678',
        },
        {
            'name': 'Frank',
            'email': 'frank@example.com',
            'password': 'FrankPass123',
            'dept': 'IT',
            'currency': 'USD',
            'username': 'frank_9012',
        },
        {
            'name': 'Grace',
            'email': 'grace@example.com',
            'password': 'GracePass456',
            'dept': 'Marketing',
            'currency': 'USD',
            'username': 'grace_3456',
        },
        {
            'name': 'Henry',
            'email': 'henry@example.com',
            'password': 'H3nryP@ss!',
            'dept': 'Sales',
            'currency': 'USD',
            'username': 'henry_7890',
        },
        {
            'name': 'Isabel',
            'email': 'isabel@example.com',
            'password': 'Is@b3lP@ss',
            'dept': 'Operations',
            'currency': 'USD',
            'username': 'isabel_2345',
        },
        {
            'name': 'Jack',
            'email': 'jack@example.com',
            'password': 'J@ckP@ss123',
            'dept': 'Finance',
            'currency': 'USD',
            'username': 'jack_6789',
        },
        {
            'name': 'Kate',
            'email': 'kate@example.com',
            'password': 'K@teP@ssword',
            'dept': 'HR',
            'currency': 'USD',
            'username': 'kate_0123',
        },
        {
            'name': 'Liam',
            'email': 'liam@example.com',
            'password': 'Li@mP@ssword',
            'dept': 'IT',
            'currency': 'USD',
            'username': 'liam_4567',
        },
        {
            'name': 'Mia',
            'email': 'mia@example.com',
            'password': 'Mi@P@ssword',
            'dept': 'Marketing',
            'currency': 'USD',
            'username': 'mia_8901',
        },
        {
            'name': 'Nathan',
            'email': 'nathan@example.com',
            'password': 'N@thanP@ss',
            'dept': 'Sales',
            'currency': 'USD',
            'username': 'nathan_2345',
        },
        {
            'name': 'Olivia',
            'email': 'olivia@example.com',
            'password': 'Olivi@P@ss',
            'dept': 'Operations',
            'currency': 'USD',
            'username': 'olivia_6789',
        },
        {
            'name': 'Patrick',
            'email': 'patrick@example.com',
            'password': 'P@trickP@ssword',
            'dept': 'Finance',
            'currency': 'USD',
            'username': 'patrick_0123',
        },
        {
            'name': 'Quinn',
            'email': 'quinn@example.com',
            'password': 'QuinnP@ssword',
            'dept': 'HR',
            'currency': 'USD',
            'username': 'quinn_4567',
        },
        {
            'name': 'Rachel',
            'email': 'rachel@example.com',
            'password': 'R@chelP@ss',
            'dept': 'IT',
            'currency': 'USD',
            'username': 'rachel_8901',
        },
        {
            'name': 'Samuel',
            'email': 'samuel@example.com',
            'password': 'S@muelP@ss',
            'dept': 'Marketing',
            'currency': 'USD',
            'username': 'samuel_2345',
        },
        {
            'name': 'Taylor',
            'email': 'taylor@example.com',
            'password': 'T@ylorP@ss',
            'dept': 'Sales',
            'currency': 'USD',
            'username': 'taylor_6789',
        },
        {
            'name': 'Uma',
            'email': 'uma@example.com',
            'password': 'Um@P@ss',
            'dept': 'Operations',
            'currency': 'USD',
            'username': 'uma_0123',
        },
        {
            'name': 'Victor',
            'email': 'victor@example.com',
            'password': 'Vict0rP@ss',
            'dept': 'Finance',
            'currency': 'USD',
            'username': 'victor_4567',
        },
        {
            'name': 'Wendy',
            'email': 'wendy@example.com',
            'password': 'WendyP@ssword',
            'dept': 'HR',
            'currency': 'USD',
            'username': 'wendy_8901',
        },
        {
            'name': 'Xavier',
            'email': 'xavier@example.com',
            'password': 'X@vierP@ss',
            'dept': 'IT',
            'currency': 'USD',
            'username': 'xavier_2345',
        },
        {
            'name': 'Yara',
            'email': 'yara@example.com',
            'password': 'Y@raP@ss',
            'dept': 'Marketing',
            'currency': 'USD',
            'username': 'yara_6789',
        },
        {
            'name': 'Zach',
            'email': 'zach@example.com',
            'password': 'Z@chP@ss',
            'dept': 'Sales',
            'currency': 'USD',
            'username': 'zach_0123',
        },
        {
            'name': 'Albert',
            'email': 'albert@example.com',
            'password': 'Alb3rtP@ss',
            'dept': 'Operations',
            'currency': 'USD',
            'username': 'albert_4567',
        },
        {
            'name': 'Beth',
            'email': 'beth@example.com',
            'password': 'B3thP@ss',
            'dept': 'Finance',
            'currency': 'USD',
            'username': 'beth_8901',
        },
        {
            'name': 'Carl',
            'email': 'carl@example.com',
            'password': 'C@rlP@ssword',
            'dept': 'HR',
            'currency': 'USD',
            'username': 'carl_2345',
        },
        {
            'name': 'Diana',
            'email': 'diana@example.com',
            'password': 'D@naP@ss',
            'dept': 'IT',
            'currency': 'USD',
            'username': 'diana_6789',
        },
        {
            'name': 'Ella',
            'email': 'ella@example.com',
            'password': 'Ell@P@ss',
            'dept': 'Marketing',
            'currency': 'USD',
            'username': 'ella_0123',
        },
        {
            'name': 'Felix',
            'email': 'felix@example.com',
            'password': 'FelixP@ss',
            'dept': 'Sales',
            'currency': 'USD',
            'username': 'felix_4567',
        },
        {
            'name': 'Gina',
            'email': 'gina@example.com',
            'password': 'Gin@P@ss',
            'dept': 'Operations',
            'currency': 'USD',
            'username': 'gina_8901',
        },
    ]
    count = 0

    usernames = [user['username'] for user in users]

    while count < 15:
        fu_username = choice(usernames)
        tu_username = choice(usernames)

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

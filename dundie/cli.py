import typer
from rich import print as bprint
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from dundie.config import settings
from dundie.db import engine
from dundie.models import (
    Balance,
    Transaction,
    User,
    Feedbacks,
    LikedPosts,
    Orders,
    Post,
    Products,
)
from dundie.utils.utils import get_username

main = typer.Typer(name='dundie CLI', add_completion=False)


@main.command()
def shell():
    """Opens interactive shell"""
    _vars = {
        'settings': settings,
        'engine': engine,
        'select': select,
        'session': Session(engine),
        'User': User,
        'Balance': Balance,
        'Transaction': Transaction,
    }
    typer.echo(f'Auto imports: {list(_vars.keys())}')
    try:
        from IPython import start_ipython

        start_ipython(
            argv=['--ipython-dir=/tmp', '--no-banner'], user_ns=_vars
        )
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


@main.command()
def user_list():
    """Lists all users"""
    table = Table(title='dundie users')
    fields = ['name', 'username', 'dept', 'email', 'currency', 'created_at']
    for header in fields:
        table.add_column(header, style='magenta')

    with Session(engine) as session:
        users = session.exec(select(User))
        for user in users:
            table.add_row(*[getattr(user, field) for field in fields])

    Console().print(table)


@main.command()
def create_user(
    name: str,
    email: str,
    password: str,
    dept: str,
    active: bool = True,
    private: bool = False,
    username: str | None = None,
    currency: str = 'USD',
):
    """Create user"""
    with Session(engine) as session:
        data = {
            'name': name,
            'email': email,
            'password': password,
            'dept': dept,
            'username': username or get_username(name),
            'currency': currency,
            'is_active': active,
            'private': private,
        }

        user = User.model_validate(data)

        session.add(user)
        session.commit()
        session.refresh(user)

        user_balance: Balance = Balance(user_id=user.id, value=0)
        session.add(user_balance)
        session.commit()
        session.refresh(user)

        typer.echo(f"Created user '{user.username}'")
        bprint(user.model_dump())
        return user


@main.command()
def transfer(points: int, username: str):
    """Transfer points to a user"""

    from dundie.controllers.transaction import check_and_transfer_points

    check_and_transfer_points(points=points, username=username)

    typer.echo(f"Transferred {points} points to '{username}'")


@main.command()
def disable_user(username):
    with Session(engine) as session:
        stmt = select(User).where(User.username == username)
        user = session.exec(stmt).first()

        user.is_active = False
        session.add(user)
        session.commit()
        session.refresh(user)
        bprint("user '{username}' deactivated")


@main.command()
def initialize():
    from dundie.xpto.random_posts import create_random_posts
    from dundie.xpto.random_transactions import create_random_transactions
    from dundie.xpto.create_users import create_test_users
    from dundie.xpto.create_products import create_initial_products

    create_test_users()
    create_random_posts()
    create_random_transactions()
    create_initial_products()

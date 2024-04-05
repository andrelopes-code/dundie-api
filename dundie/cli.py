import typer
from rich import print as bprint
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select

from dundie.config import settings
from dundie.db import engine
from dundie.models import User, Balance
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
            'currency': currency
        }

        user = User.model_validate(data)

        session.add(user)
        session.commit()
        session.refresh(user)

        user_balance: Balance = Balance(
            user_id=user.id,
            value=0
        )
        session.add(user_balance)
        session.commit()
        session.refresh(user)

        typer.echo(f"created user '{user.username}'")
        bprint(user.model_dump())
        return user

from __future__ import annotations
import unicodedata
from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from dundie.security import HashedPassword

# Fixes the 'circular import' problem
if TYPE_CHECKING:
    from typing import List
    from dundie.models.transaction import Transaction, Balance


class User(SQLModel, table=True):
    """Represents a user in the database."""

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False)
    username: str = Field(max_length=255, unique=True, nullable=False)
    avatar: str | None = None
    bio: str | None = None
    password: HashedPassword = Field(nullable=False)
    name: str = Field(max_length=255, nullable=False)
    dept: str = Field(max_length=255, nullable=False)
    currency: str = Field(nullable=False)
    last_password_change: datetime | None = Field(default=None)

    # Define 'incomes' como uma lista opcional de instâncias de 'Transaction'.
    # Estabelece o relacionamento com base em 'user_id' de Transaction igual a
    # 'id' de User ('primaryjoin'). Relacionamento bidirecional, permitindo
    # o acesso a todas as transações associadas a um usuário que recebeu renda
    # ('back_populates').
    incomes: List[Transaction] | None = Relationship(
        back_populates='user',
        sa_relationship_kwargs={
            'primaryjoin': 'User.id == Transaction.user_id'
        }
    ),
    # Define 'expenses' como uma lista opcional de 'Transaction'. Estabelece o
    # relacionamento com base em 'from_id' de Transaction igual a 'id' de User
    # ('primaryjoin'). Relacionamento bidirecional, permitindo o acesso a todas
    # as transações associadas a um usuário que realizou despesas
    # ('back_populates').
    expenses: List[Transaction] | None = Relationship(
        back_populates='from_user',
        sa_relationship_kwargs={
            'primaryjoin': 'User.id == Transaction.from_id'
        }
    )

    _balance: Balance | None = Relationship(
        back_populates='user',
        sa_relationship_kwargs={'lazy': 'dynamic'}
    )

    @property
    def superuser(self):
        return self.dept == 'management'

    @property
    def balance(self):
        if (user_balance := self._balance.first()) is not None:
            return user_balance.value
        return 0


def get_username(name: str) -> str:
    """
    Converts a given name into a username-friendly format by removing accents
    and spaces, and converting it to lowercase.

    Args:
        name (str): The input name to be converted into a username.

    Returns:
        str: The username-friendly version of the input name.
    """
    # Convert name to lowercase and replace spaces with hyphens
    name = name.lower().replace(' ', '-')

    chars = []

    for c in unicodedata.normalize('NFD', name):
        if unicodedata.category(c) != 'Mn':
            chars.append(c)

    return ''.join(chars)

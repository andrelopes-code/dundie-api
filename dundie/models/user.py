import unicodedata
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

from dundie.security import HashedPassword

if TYPE_CHECKING:
    from .transaction import Transaction, Balance


class User(SQLModel, table=True):
    """Represents a user in the database."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False)
    username: str = Field(max_length=255, unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: HashedPassword = Field(nullable=False)
    name: str = Field(max_length=255, nullable=False)
    dept: str = Field(max_length=255, nullable=False)
    currency: str = Field(nullable=False)
    last_password_change: datetime | None = Field(default=None)

    # Populates a `.user` on `Transaction`
    incomes: Optional[list["Transaction"]] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "primaryjoin": 'User.id == Transaction.user_id'
        },
    )
    # Populates a `.from_user` on `Transaction`
    expenses: Optional[list["Transaction"]] = Relationship(
        back_populates="from_user",
        sa_relationship_kwargs={
            "primaryjoin": 'User.id == Transaction.from_id'
        },
    )
    # Populates a `.user` on `Balance`
    _balance: Optional["Balance"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "dynamic"}
    )

    @property
    def balance(self) -> int:
        """Returns the current balance of the user"""
        if (user_balance := self._balance.first()) is not None:
            return user_balance.value
        return 0

    @property
    def superuser(self):
        return self.dept == 'management'


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

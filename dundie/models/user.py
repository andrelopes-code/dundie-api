from datetime import datetime
from dundie.utils.utils import get_utcnow
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

from dundie.security import HashedPassword

if TYPE_CHECKING:
    from .transaction import Transaction, Balance


class User(SQLModel, table=True):
    """Represents a user in the database."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False)
    username: str = Field(
        max_length=255,
        unique=True,
        nullable=False,
        index=True
    )
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: HashedPassword = Field(nullable=False)
    name: str = Field(max_length=255, nullable=False)
    dept: str = Field(max_length=255, nullable=False)
    currency: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=get_utcnow,
        nullable=False
    )
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

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from dundie.security import HashedPassword
from dundie.utils.utils import get_utcnow

if TYPE_CHECKING:
    from .transaction import Balance, Transaction
    from .posts import Post


class User(SQLModel, table=True):
    """Represents a user in the database."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False)
    username: str = Field(
        max_length=255, unique=True, nullable=False, index=True
    )
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: HashedPassword = Field(nullable=False)
    name: str = Field(max_length=255, nullable=False)
    dept: str = Field(max_length=255, nullable=False)
    github: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    currency: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=get_utcnow, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    private: bool = Field(default=False, nullable=False)
    last_password_change: Optional[datetime] = Field(default=None)

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
        back_populates="user", sa_relationship_kwargs={"lazy": "select"}
    )
    # Populates a `.user` on `Post`
    posts: Optional[list["Post"]] = Relationship(
        back_populates="user", sa_relationship_kwargs={
            "primaryjoin": 'User.id == Post.user_id'
        }
    )

    @property
    def balance(self) -> int:
        """Returns the current balance of the user"""
        return self._balance.value

    @property
    def superuser(self):
        return self.dept == 'management'

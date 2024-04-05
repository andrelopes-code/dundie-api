from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from dundie.utils.utils import get_utcnow

if TYPE_CHECKING:
    from dundie.models.user import User


class Transaction(SQLModel, table=True):
    """Represents the Transaction Model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    from_id: int = Field(foreign_key="user.id", nullable=False)
    value: int = Field(nullable=False)
    date: datetime = Field(default_factory=get_utcnow, nullable=False)

    # Populates a `.incomes` on `User`
    user: Optional["User"] = Relationship(
        back_populates="incomes",
        sa_relationship_kwargs={
            "primaryjoin": 'Transaction.user_id == User.id'
        },
    )
    # Populates a `.expenses` on `User`
    from_user: Optional["User"] = Relationship(
        back_populates="expenses",
        sa_relationship_kwargs={
            "primaryjoin": 'Transaction.from_id == User.id'
        },
    )

    def transfer_points(self):
        print("TRANSFER_POINTS_CHECK")


class Balance(SQLModel, table=True):
    """Store the balance of a user account"""

    user_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        primary_key=True,
        unique=True,
    )
    value: int = Field(nullable=False, ge=0)
    updated_at: datetime = Field(
        default_factory=get_utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": get_utcnow},
    )

    # Populates a `._balance` on `User`
    user: Optional["User"] = Relationship(back_populates="_balance")

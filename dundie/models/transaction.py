from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

# Fixes the 'circular import' problem
if TYPE_CHECKING:
    from dundie.models.user import User


class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(foreign_key='user.id', nullable=False)
    from_id: int | None = Field(foreign_key='user.id', nullable=False)
    value: int = Field(nullable=False)
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Define 'user' como instância opcional de 'User'. O relacionamento é
    # estabelecido com base em 'user_id' de Transaction igual a 'id' de User
    # ('primaryjoin'). Relacionamento bidirecional, permitindo acesso a
    # transações associadas a um usuário ('back_populates').
    user: Optional[User] = Relationship(
        back_populates='incomes',
        sa_relationship_kwargs={
            'primaryjoin': 'Transaction.user_id == User.id'
        }
    ),
    # Define 'from_user' como instância opcional de 'User'. O relacionamento é
    # estabelecido com base em 'from_id' de Transaction igual a 'id' de User
    # ('primaryjoin'). Relacionamento bidirecional, permitindo acesso a
    # transações associadas ao usuário que realizou a despesa
    # ('back_populates').
    from_user: Optional[User] = Relationship(
        back_populates='expenses',
        sa_relationship_kwargs={
            'primaryjoin': 'Transaction.from_id == User.id'
        }
    )


class Balance(SQLModel, table=True):
    user_id: int = Field(
        foreign_key='user.id',
        nullable=False,
        primary_key=True,
        unique=True
    )
    value: int = Field(nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={
            'onupdate': lambda: datetime.now(timezone.utc)
        }
    )

    user: Optional[User] = Relationship(
        back_populates='_balance'
    )

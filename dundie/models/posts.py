from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import ForeignKeyConstraint
from dundie.utils.utils import get_utcnow

if TYPE_CHECKING:
    from dundie.models.user import User


class Post(SQLModel, table=True):
    """Represents a post made by a user."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, index=True)
    content: str = Field(max_length=1000, nullable=False)
    likes: int = Field(default=0, nullable=False)
    date: datetime = Field(default_factory=get_utcnow, nullable=False)

    # Populates a `.posts` on `User`
    user: Optional["User"] = Relationship(
        back_populates="posts",
        sa_relationship_kwargs={
            "primaryjoin": 'Post.user_id == User.id'
        },
    )


class LikedPosts(SQLModel, table=True):
    """Represents posts liked by a user."""

    user_id: int = Field(
        foreign_key="user.id",
        primary_key=True,
        index=True,
        nullable=False
    )
    post_id: int = Field(
        foreign_key="post.id",
        primary_key=True,
        index=True,
        nullable=False,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["post_id"],
            ["post.id"],
            name="likedposts_post_id_fkey",
            ondelete="CASCADE"
        ),
    )

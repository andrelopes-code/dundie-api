from fastapi import APIRouter, HTTPException
from dundie.models import Post
from dundie.models import User
from typing import List
from dundie.serializers.post import PostResponse, PostRequest
from dundie.db import ActiveSession, Session
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from dundie.auth.functions import AuthenticatedUser

router = APIRouter()


@router.get(
    '/post',
    dependencies=[AuthenticatedUser],
    response_model=List[PostResponse]
)
async def get_posts(
    sort: str | None = None,
    session: Session = ActiveSession
):
    """Get posts from database"""

    # Select all posts from the database
    stmt = (
        select(Post)
        .options(joinedload(Post.user))
        .order_by(Post.date.desc())
    )
    posts = session.exec(statement=stmt).all()

    return posts


@router.post('/post', response_model=PostResponse)
def create_new_post(
    post_data: PostRequest,
    user: User = AuthenticatedUser,
    session: Session = ActiveSession
):
    """Creates a new post in the database """

    new_post = Post(content=post_data.content, user_id=user.id, likes=0)

    session.add(new_post)
    try:
        session.commit()
        session.refresh(new_post)
    except IntegrityError:
        session.rollback()
        raise HTTPException(500, 'Database IntegrityError')

    return new_post

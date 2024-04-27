from fastapi import APIRouter, HTTPException
from dundie.models import Post
from dundie.models import User, LikedPosts
from typing import List
from dundie.serializers.post import PostResponse, PostRequest
from dundie.db import ActiveSession, Session
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from dundie.auth.functions import AuthenticatedUser
from dundie.controllers.post import check_post_is_liked

router = APIRouter()


@router.get(
    '/post',
    response_model=List[PostResponse]
)
async def get_posts(
    sort: str | None = None,
    user: User = AuthenticatedUser,
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

    posts_with_liked = [
        {
            **post.model_dump(),
            'user': post.user.model_dump(),
            'liked': check_post_is_liked(user, post.id, session)
        }
        for post in posts
    ]

    return posts_with_liked


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


@router.delete('/post/{post_id}')
def delete_post(
    post_id: int,
    user: User = AuthenticatedUser,
    session: Session = ActiveSession
):
    """Deletes a post from the database """

    # Checks if there is a post with that id
    stmt = select(Post).where(Post.id == post_id)
    post = session.exec(stmt).first()
    if not post:
        raise HTTPException(404, 'Post not found')

    if post.user_id != user.id and not user.superuser:
        raise HTTPException(403, 'You are not allowed to delete this post')

    session.delete(post)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(500, e.orig.diag.message_detail)

    return {"detail": "post deleted successfully"}


@router.post('/post/{post_id}/like')
def like_post(
    post_id: int,
    user: User = AuthenticatedUser,
    session: Session = ActiveSession
):
    """Creates a new post in the database """

    # Checks if there is already a post with that id
    stmt = select(Post).where(Post.id == post_id)
    post = session.exec(stmt).first()
    if not post:
        raise HTTPException(404, 'Post not found')

    # Checks if the user has already liked the post
    if check_post_is_liked(post_id=post_id, user=user, session=session):
        raise HTTPException(409, 'Post already liked')

    post_liked = LikedPosts(post_id=post_id, user_id=user.id)
    post.likes += 1
    session.add(post_liked)
    session.add(post)

    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(500, e.orig.diag.message_detail)

    return {"detail": "post liked successfully"}


@router.delete('/post/{post_id}/like')
def unlike_post(
    post_id: int,
    user: User = AuthenticatedUser,
    session: Session = ActiveSession
):
    """Deletes a post from the database """

    # Checks if there is already a post with that id
    stmt = select(Post).where(Post.id == post_id)
    post = session.exec(stmt).first()
    if not post:
        raise HTTPException(404, 'Post not found')

    # Checks if the user has already liked the post
    liked_post = check_post_is_liked(
        post_id=post_id,
        user=user,
        session=session,
        notbool=True
    )
    if not liked_post:
        raise HTTPException(404, 'Post not liked')

    post.likes -= 1

    session.add(post)
    session.delete(liked_post)

    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(500, e.orig.diag.message_detail)

    return {"detail": "post unliked successfully"}

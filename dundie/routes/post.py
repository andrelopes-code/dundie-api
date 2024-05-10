from fastapi import APIRouter, HTTPException, Depends
from dundie.models import Post
from dundie.models import User, LikedPosts
from typing import Literal
from dundie.serializers.post import PagePostResponse, PostRequest, PostResponse
from dundie.db import ActiveSession, Session
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from dundie.auth.functions import AuthenticatedUser
from dundie.controllers.post import check_post_is_liked
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate

router = APIRouter()


@router.get(
    '/post',
    response_model=PagePostResponse
)
async def get_posts(
    sort: Literal[
        'date_asc',
        'date_desc',
        'like_asc',
        'like_desc'
    ] = 'date_desc',
    user: User = AuthenticatedUser,
    session: Session = ActiveSession,
    params: Params = Depends(),
):
    """Get posts from database"""

    # Base statement to get all posts
    stmt_base = select(Post)

    # Define the sort order and add it to the statement
    match sort:
        case 'date_asc':
            stmt = stmt_base.order_by(Post.date.asc())
        case 'date_desc':
            stmt = stmt_base.order_by(Post.date.desc())
        case 'like_asc':
            stmt = stmt_base.order_by(Post.likes.asc(), Post.id.asc())
        case 'like_desc':
            stmt = stmt_base.order_by(Post.likes.desc(), Post.id.asc())

    result = paginate(
        query=stmt,
        params=params,
        session=session,
    )

    # Adjust the data to be returned
    result.items = [
        {
            "id": post.id,
            "date": post.date,
            "content": post.content,
            "user": {
                "id": post.user.id,
                "name": post.user.name,
                "username": post.user.username,
                "dept": post.user.dept,
                "avatar": post.user.avatar
            },
            "likes": post.likes,
            "liked": check_post_is_liked(user, post.id, session)
        }
        for post in result.items
    ]

    posts = result.__dict__
    posts.update({'sort': sort})

    return posts


@router.post('/post', response_model=PostResponse)
async def create_new_post(
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
async def delete_post(
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
async def like_post(
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
async def unlike_post(
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

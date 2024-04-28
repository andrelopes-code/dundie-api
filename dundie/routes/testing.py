from fastapi import APIRouter, HTTPException, Depends
from dundie.models import Post
from dundie.models import User, LikedPosts
from typing import List
from dundie.serializers.post import PostResponse, PostRequest
from dundie.db import ActiveSession, Session, engine
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from dundie.auth.functions import AuthenticatedUser
from dundie.controllers.post import check_post_is_liked
from dundie.xpto.random_posts import create_random_posts
from dundie.xpto.random_like_posts import random_like_posts
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from rich import print as pp

router = APIRouter()

@router.get('/test')
def teste(params: Params = Depends(), session: Session = ActiveSession):
    stmt = select(User)
    page_users = paginate(query=stmt, params=params, session=session)
    
    page_users.items = [
        {'username': user.username, 'name': user.name} for user in page_users.items
    ]
    
    return page_users

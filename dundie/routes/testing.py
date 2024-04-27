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
from dundie.xpto.random_posts import create_random_posts
from dundie.xpto.random_like_posts import random_like_posts

router = APIRouter()

@router.get('/test')
def teste():
    return random_like_posts()

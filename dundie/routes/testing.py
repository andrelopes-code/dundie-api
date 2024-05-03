from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from dundie.xpto.random_posts import create_random_posts
from dundie.xpto.random_like_posts import random_like_posts
from dundie.xpto.random_transactions import create_random_transactions
from dundie.xpto.create_users import create_test_users
from rich import print as pp

router = APIRouter()

@router.get('/test/random-posts')
def teste():
    return create_random_posts()


@router.get('/test/random-likes')
def teste():
    return random_like_posts(None)


@router.get('/test/random-users')
def teste():
    return create_test_users()


@router.get('/test/random-transactions')
def teste():
    return create_random_transactions()

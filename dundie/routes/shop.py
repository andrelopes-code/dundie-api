from fastapi import APIRouter, HTTPException
from dundie.models import Products, User, Orders, Balance
from dundie.serializers.shop import ProductResponse
from dundie.db import ActiveSession, Session
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from dundie.auth.functions import AuthenticatedUser

router = APIRouter()


@router.get(
    '/shop/products',
    response_model=list[ProductResponse],
)
async def get_products(
    session: Session = ActiveSession,
    user: User = AuthenticatedUser
):
    """Get products from database"""

    stmt = select(Products)
    result = session.exec(stmt).all()
    return result


@router.post(
    '/shop/{product_id}/buy',
)
async def buy_product(
    product_id: int,
    user: User = AuthenticatedUser,
    session: Session = ActiveSession
):
    product = session.get(Products, product_id)
    balance = session.get(Balance, user.id)

    if not product:
        raise HTTPException(404, 'Product not found')

    if product.price > balance.value:
        raise HTTPException(400, 'Not enough balance')

    order = Orders(
        user_id=user.id,
        product_id=product.id,
        product=product.name,
        product_img=product.image,
        name=user.name,
    )
    balance.value -= product.price
    session.add(balance)
    session.add(order)

    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(500, e.orig.diag.message_detail)

    return {"detail": "product bought successfully"}

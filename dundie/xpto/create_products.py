
from dundie.db import engine
from dundie.serializers.shop import ProductRequest
from dundie.models import User, Products
from sqlmodel import Session, select


def create_initial_products():
    with Session(engine) as session:
        
        products = [
            Products(
            name='Dunder Mifflin Planner',
            description='Planner',
            image='https://http2.mlstatic.com/D_NQ_NP_2X_621010-MLB51657001235_092022-F.webp',
            price=399
        ),
            Products(
            name='Black Dunder Mifflin T-Shirt',
            description='T-Shirt',
            image='https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcRvoQHGi4n6eM2pIu30KwtN466HBPR_FgwNk7YRmBW8bwtlDl4YaTyAP6JIxV1jLi2B4cw6mFVRJea2Ucc3gnZs1dVav_xNArN4vZPh2kGq-8GeKTUsCw8Q&usqp=CAY',
            price=699
        ),
            Products(
            name='Dunder Mifflin Mug',
            description='Mug',
            image='https://acdn.mitiendanube.com/stores/001/991/736/products/dunder-miflin-fundo-branco-76ec526d6975677bfe169747445159081-ca57732782b5bab94f16974744702759-1024-1024.webp',
            price=599
        ),
        ]
        
        for product in products:
            try:
                session.add(product)
                session.commit()
            except Exception as e:
                session.rollback()
                print(e)
    
    
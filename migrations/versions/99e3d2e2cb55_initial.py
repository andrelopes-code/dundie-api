"""empty message

Revision ID: 99e3d2e2cb55
Revises: 
Create Date: 2024-05-16 08:08:31.485723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '99e3d2e2cb55'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ! FEEDBACKS TABLE
    op.create_table('feedbacks',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('feedback', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedbacks_created_at'), 'feedbacks', ['created_at'], unique=False)
    
    # ! PRODUCTS TABLE
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('image', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    
    # ! USERS TABLE
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('avatar', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('bio', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('dept', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('github', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('linkedin', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('instagram', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('currency', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('private', sa.Boolean(), nullable=False),
    sa.Column('last_password_change', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email', name='uq_user_email'),
    sa,UniqueConstraint('username', name='uq_user_username'),
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    
    # ! BALANCE TABLE
    op.create_table('balance',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_balance_value'), 'balance', ['value'], unique=False)
    
    # ! ORDERS TABLE
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('product', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('product_img', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_created_at'), 'orders', ['created_at'], unique=False)
    op.create_index(op.f('ix_orders_status'), 'orders', ['status'], unique=False)
    
    # ! POST TABLE
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('content', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('likes', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_user_id'), 'post', ['user_id'], unique=False)
    op.create_index(op.f('ix_post_date'), 'post', ['date'], unique=False)
    op.create_index(op.f('ix_post_likes'), 'post', ['likes'], unique=False)
    
    # ! TRANSACTION TABLE
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('from_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['from_id'], ['user.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transaction_user_id'), 'transaction', ['user_id'], unique=False)
    op.create_index(op.f('ix_transaction_from_id'), 'transaction', ['from_id'], unique=False)
    op.create_index(op.f('ix_transaction_date'), 'transaction', ['date'], unique=False)
    op.create_index(op.f('ix_transaction_value'), 'transaction', ['value'], unique=False)
    
    # ! LIKEDPOSTS TABLE
    op.create_table('likedposts',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'post_id')
    )
    op.create_index(op.f('ix_likedposts_post_id'), 'likedposts', ['post_id'], unique=False)
    op.create_index(op.f('ix_likedposts_user_id'), 'likedposts', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_likedposts_user_id'), table_name='likedposts')
    op.drop_index(op.f('ix_likedposts_post_id'), table_name='likedposts')
    op.drop_table('likedposts')
    op.drop_table('transaction')
    op.drop_index(op.f('ix_post_user_id'), table_name='post')
    op.drop_table('post')
    op.drop_index(op.f('ix_orders_status'), table_name='orders')
    op.drop_index(op.f('ix_orders_created_at'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_balance_value'), table_name='balance')
    op.drop_table('balance')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    op.drop_table('products')
    op.drop_table('feedbacks')
    # ### end Alembic commands ###

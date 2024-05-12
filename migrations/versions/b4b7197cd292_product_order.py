"""empty message

Revision ID: b4b7197cd292
Revises: d5d5b51e056f
Create Date: 2024-05-09 22:54:45.738301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b4b7197cd292'
down_revision: Union[str, None] = 'd5d5b51e056f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('product', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('orders', sa.Column('product_img', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.create_index(op.f('ix_orders_created_at'), 'orders', ['created_at'], unique=False)
    op.create_index(op.f('ix_orders_status'), 'orders', ['status'], unique=False)
    op.alter_column('products', 'description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('products', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('products', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('products', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('products', 'description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_index(op.f('ix_orders_status'), table_name='orders')
    op.drop_index(op.f('ix_orders_created_at'), table_name='orders')
    op.drop_column('orders', 'product_img')
    op.drop_column('orders', 'product')
    # ### end Alembic commands ###
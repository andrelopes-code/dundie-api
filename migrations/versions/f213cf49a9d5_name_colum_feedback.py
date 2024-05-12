"""name_colum_feedback

Revision ID: f213cf49a9d5
Revises: b4b7197cd292
Create Date: 2024-05-11 22:28:23.207951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f213cf49a9d5'
down_revision: Union[str, None] = 'b4b7197cd292'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feedbacks', sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.drop_constraint('orders_product_id_fkey', 'orders', type_='foreignkey')
    op.create_foreign_key(None, 'orders', 'products', ['product_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'orders', type_='foreignkey')
    op.create_foreign_key('orders_product_id_fkey', 'orders', 'products', ['product_id'], ['id'], ondelete='CASCADE')
    op.drop_column('feedbacks', 'name')
    # ### end Alembic commands ###

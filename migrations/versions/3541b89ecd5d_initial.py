"""Initial

Revision ID: 3541b89ecd5d
Revises:
Create Date: 2024-03-27 12:06:17.275896
"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3541b89ecd5d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            'username', sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column('avatar', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('bio', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            'password', sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('dept', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            'currency', sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###

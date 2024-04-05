"""criar_system_user

Revision ID: 760d6dfdefe7
Revises: 91f7356420d1
Create Date: 2024-04-05 11:39:59.580704

"""

import sqlmodel
from sqlalchemy.exc import IntegrityError
from alembic import op
from typing import Sequence, Union
from dundie.models import User
from dundie.config import settings

# revision identifiers, used by Alembic.
revision: str = '760d6dfdefe7'
down_revision: Union[str, None] = '91f7356420d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = sqlmodel.Session(bind=bind)
    admin = User(
        name="Admin",
        username="admin",
        email="admin@admin",
        dept="management",
        password=settings.security.ADMIN_PASS,
        currency="USD"
    )

    pdm = User(
        name="PointDeliveryMan",
        username="pointdeliveryman",
        email="pointdeliveryman@system",
        dept="management",
        password=settings.security.DELIVERY_PASS,
        currency="USD"
    )

    try:
        session.add(admin)
        session.add(pdm)
        session.commit()
    except IntegrityError:
        session.rollback()


def downgrade() -> None:
    pass

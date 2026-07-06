"""add_product_tags_many_to_many

Revision ID: bc5ea4d74eb2
Revises: 4cc59002d1bc
Create Date: 2026-02-23 17:32:10.207503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc5ea4d74eb2'
down_revision: Union[str, None] = '4cc59002d1bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

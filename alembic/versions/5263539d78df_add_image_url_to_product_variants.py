"""add image_url to product_variants

Revision ID: 5263539d78df
Revises: 66e02f4f7834
Create Date: 2026-02-14 10:53:48.471003

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '5263539d78df'
down_revision = '66e02f4f7834'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [col["name"] for col in inspector.get_columns("product_variants")]

    if "image_url" not in columns:
        op.add_column(
            "product_variants",
            sa.Column("image_url", sa.String(), nullable=True)
        )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [col["name"] for col in inspector.get_columns("product_variants")]

    if "image_url" in columns:
        op.drop_column("product_variants", "image_url")
"""Add a global superadmin flag to users.

Revision ID: 0002_superadmin
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_superadmin"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("is_superadmin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "is_superadmin", server_default=None)


def downgrade():
    op.drop_column("users", "is_superadmin")

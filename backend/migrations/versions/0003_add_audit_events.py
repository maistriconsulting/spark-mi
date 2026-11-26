"""Add the administrative audit log.

Revision ID: 0003_audit_events
Revises: 0002_superadmin
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_audit_events"
down_revision = "0002_superadmin"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target_type", sa.String(24), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_events_actor_user_id", "audit_events", ["actor_user_id"])
    op.create_index("ix_audit_events_tenant_id", "audit_events", ["tenant_id"])


def downgrade():
    op.drop_table("audit_events")

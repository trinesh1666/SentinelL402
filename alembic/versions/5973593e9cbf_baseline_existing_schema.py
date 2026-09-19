"""create initial SentinelL402 schema

Revision ID: 5973593e9cbf
Revises:
Create Date: 2026-09-06 11:45:31.030084
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5973593e9cbf"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial SentinelL402 database schema."""

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
         sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_users_user_id",
        "users",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "api_keys",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "key_hash",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "active",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "last_used_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_api_keys_id",
        "api_keys",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_api_keys_key_hash",
        "api_keys",
        ["key_hash"],
        unique=True,
    )

    op.create_table(
        "accounts",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "credits",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "total_requests",
            sa.Integer(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_index(
        "ix_accounts_id",
        "accounts",
        ["id"],
        unique=False,
    )

    op.create_table(
        "usage_records",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "request_type",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "credits_used",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_usage_records_id",
        "usage_records",
        ["id"],
        unique=False,
    )

    op.create_table(
        "payments",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "amount_sats",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "payment_hash",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "invoice",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "credits_granted",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_hash"),
        sa.UniqueConstraint("invoice"),
    )

    op.create_index(
        "ix_payments_id",
        "payments",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the initial SentinelL402 database schema."""

    op.drop_index(
        "ix_payments_id",
        table_name="payments",
    )

    op.drop_table("payments")

    op.drop_index(
        "ix_usage_records_id",
        table_name="usage_records",
    )

    op.drop_table("usage_records")

    op.drop_index(
        "ix_accounts_id",
        table_name="accounts",
    )

    op.drop_table("accounts")

    op.drop_index(
        "ix_api_keys_key_hash",
        table_name="api_keys",
    )

    op.drop_index(
        "ix_api_keys_id",
        table_name="api_keys",
    )

    op.drop_table("api_keys")

    op.drop_index(
        "ix_users_user_id",
        table_name="users",
    )

    op.drop_index(
        "ix_users_id",
        table_name="users",
    )

    op.drop_table("users")
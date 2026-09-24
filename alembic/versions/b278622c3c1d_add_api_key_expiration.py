"""add api key expiration

Revision ID: b278622c3c1d
Revises: 73105a708303
Create Date: 2026-09-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b278622c3c1d"
down_revision: Union[str, Sequence[str], None] = "73105a708303"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add optional expiration timestamp to API keys."""
    op.add_column(
        "api_keys",
        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove API key expiration timestamp."""
    op.drop_column(
        "api_keys",
        "expires_at",
    )
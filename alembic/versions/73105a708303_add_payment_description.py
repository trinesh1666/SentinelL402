"""add payment description

Revision ID: 73105a708303
Revises: 5973593e9cbf
Create Date: 2026-09-06 12:03:05.098329

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "73105a708303"
down_revision: Union[str, Sequence[str], None] = "5973593e9cbf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add description column to payments."""
    op.add_column(
        "payments",
        sa.Column(
            "description",
            sa.String(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove description column from payments."""
    op.drop_column(
        "payments",
        "description",
    )
"""baseline existing schema

Revision ID: 5973593e9cbf
Revises:
Create Date: 2026-09-06 11:45:31.030084

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "5973593e9cbf"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Baseline migration.

    The database already contains the current schema and production/demo data.
    Therefore this migration intentionally performs no schema changes.
    """
    pass


def downgrade() -> None:
    """
    Baseline migration.

    No downgrade operation is performed because this migration only records
    the existing database state.
    """
    pass
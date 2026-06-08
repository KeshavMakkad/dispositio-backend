"""add print tracking to seatings

Revision ID: b2c3d4e5f6a7
Revises: 70a301bdbd07
Create Date: 2026-06-03 01:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "70a301bdbd07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "seatings",
        sa.Column(
            "is_printed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        schema="public",
    )
    op.add_column(
        "seatings",
        sa.Column("printed_at", sa.DateTime(timezone=True), nullable=True),
        schema="public",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("seatings", "printed_at", schema="public")
    op.drop_column("seatings", "is_printed", schema="public")

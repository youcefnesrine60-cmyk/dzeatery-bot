"""add_updated_at_to_subscriptions

Revision ID: dc626cfd1aaf
Revises: fd29befe8baf
Create Date: 2026-08-15 12:27:32.236360

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "dc626cfd1aaf"
down_revision: Union[str, Sequence[str], None] = "fd29befe8baf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """
    إضافة عمود updated_at إلى جدول subscriptions.
    """
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # ✅ التحقق من وجود العمود
    columns = [col["name"] for col in inspector.get_columns("subscriptions")]
    
    if "updated_at" not in columns:
        # ✅ إضافة العمود مع تحديث تلقائي
        op.add_column(
            "subscriptions",
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=True,
                server_default=sa.text("now()"),
                comment="تاريخ ووقت آخر تحديث",
            )
        )
        print("[OK] Added updated_at column to subscriptions")
    else:
        print("[INFO] updated_at column already exists in subscriptions")


def downgrade() -> None:
    """
    حذف عمود updated_at من جدول subscriptions.
    """
    op.drop_column("subscriptions", "updated_at")

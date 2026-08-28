"""record_payments_user_id_field

Revision ID: 48b7a91adb30
Revises: 2d999b8ed18f
Create Date: 2026-08-13 13:23:11.754717

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "48b7a91adb30"
down_revision: Union[str, Sequence[str], None] = "2d999b8ed18f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """
    Recording the addition of the user_id column to the payments table.

    Note: The column and index have already been added manually.

    This posting is only to record the change in the Alembic date.

    """

    #  Post is empty - the changes already exist in the database.
    pass


def downgrade() -> None:
    """ 
    Record undo adding user_id column. 

    Note: This posting is empty - rollback is handled in a separate posting. 

    """
    # Post is empty - rollback is done in a separate posting if necessary
    pass
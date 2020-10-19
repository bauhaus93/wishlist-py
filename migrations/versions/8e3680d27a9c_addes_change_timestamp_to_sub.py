"""Addes change timestamp to sub

Revision ID: 8e3680d27a9c
Revises: dd9419262aa5
Create Date: 2020-10-19 14:27:18.957536

"""
import time

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8e3680d27a9c"
down_revision = "dd9419262aa5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("subscription", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "notification_timestamp",
                sa.Integer(),
                server_default=str(int(time.time())),
                nullable=False,
            )
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("subscription", schema=None) as batch_op:
        batch_op.drop_column("notification_timestamp")

    # ### end Alembic commands ###

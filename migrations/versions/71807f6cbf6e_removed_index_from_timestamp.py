"""Removed index from timestamp

Revision ID: 71807f6cbf6e
Revises: 03d4e872c858
Create Date: 2020-10-13 14:58:43.681129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71807f6cbf6e'
down_revision = '03d4e872c858'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_wishlist_timestamp', table_name='wishlist')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_wishlist_timestamp', 'wishlist', ['timestamp'], unique=False)
    # ### end Alembic commands ###

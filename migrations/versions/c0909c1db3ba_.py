"""empty message

Revision ID: c0909c1db3ba
Revises: 0f282f56e450
Create Date: 2021-01-28 11:36:09.609716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0909c1db3ba'
down_revision = '0f282f56e450'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('show_time', sa.DateTime(), nullable=False))
    op.drop_column('show', 'start_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('start_time', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('show', 'show_time')
    # ### end Alembic commands ###

"""empty message

Revision ID: c228dbca2a94
Revises: 7ef15d0d63ab
Create Date: 2021-01-28 07:41:55.226888

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c228dbca2a94'
down_revision = '7ef15d0d63ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('country', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'country')
    # ### end Alembic commands ###
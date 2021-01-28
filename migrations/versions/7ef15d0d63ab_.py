"""empty message

Revision ID: 7ef15d0d63ab
Revises: b0616c1faad4
Create Date: 2021-01-28 07:29:31.902680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ef15d0d63ab'
down_revision = 'b0616c1faad4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('seek_description', sa.String(length=500), nullable=True))
    op.add_column('venue', sa.Column('seek_talent', sa.Boolean(), nullable=True))
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('description', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('venue', 'seek_talent')
    op.drop_column('venue', 'seek_description')
    # ### end Alembic commands ###

"""change publisher with author col

Revision ID: c8ae6ca0b280
Revises: 73e198f75d33
Create Date: 2022-05-02 14:03:04.465553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8ae6ca0b280'
down_revision = '73e198f75d33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('author', sa.String(), nullable=True))
    op.drop_column('articles', 'publisher')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('articles', sa.Column('publisher', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('articles', 'author')
    # ### end Alembic commands ###
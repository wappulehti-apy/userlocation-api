"""initial

Revision ID: d1542e3762c1
Revises:
Create Date: 2019-04-14 15:51:52.100483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1542e3762c1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('locations',
                    sa.Column('id', sa.Integer(), autoincrement=False, nullable=False),
                    sa.Column('public_id', sa.String(), nullable=False),
                    sa.Column('created_date', sa.DateTime(), nullable=False),
                    sa.Column('latitude', sa.Numeric(precision=8, asdecimal=False), nullable=True),
                    sa.Column('longitude', sa.Numeric(precision=8, asdecimal=False), nullable=True),
                    sa.Column('initials', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('locations')
    # ### end Alembic commands ###
"""user table

Revision ID: 67635238bfab
Revises: 
Create Date: 2020-05-28 09:19:09.104527

"""
from alembic import op
import sqlalchemy as sa

from apollo.lib.types.uuid import UUID

# revision identifiers, used by Alembic.
revision = '67635238bfab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', UUID(length=36), nullable=False),
        sa.Column('password_hash', sa.String(119), nullable=False),
        sa.Column('password_salt', sa.String(29), nullable=False),
    )
    
def downgrade():
    op.drop_table('user')

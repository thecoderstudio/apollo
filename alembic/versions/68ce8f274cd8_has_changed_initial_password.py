"""empty message

Revision ID: 68ce8f274cd8
Revises: 12a9aec438b3
Create Date: 2020-09-03 12:26:32.295600

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '68ce8f274cd8'
down_revision = '12a9aec438b3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column(
        'has_changed_initial_password', sa.Boolean, default=False))


def downgrade():
    op.drop_column('user', 'has_changed_initial_password')

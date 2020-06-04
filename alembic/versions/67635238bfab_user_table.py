"""user table

Revision ID: 67635238bfab
Revises:
Create Date: 2020-05-28 09:19:09.104527

"""
import logging
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from apollo.lib.hash import hash_plaintext


log = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision = '67635238bfab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    user_table = op.create_table(
        'user',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(36), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(119), nullable=False),
        sa.Column('password_salt', sa.String(29), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('user')

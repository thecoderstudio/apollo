"""user table

Revision ID: 67635238bfab
Revises: 
Create Date: 2020-05-28 09:19:09.104527

"""
import logging
import secrets
import string
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

    add_user(user_table)


def downgrade():
    op.drop_table('user')


def randompassword():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(12))


def add_user(user_table):
    password = randompassword()
    password_hash, password_salt = hash_plaintext(password)

    user = {
        'id': uuid.uuid4(),
        'username': 'admin',
        'password_hash': password_hash,
        'password_salt': password_salt
    }

    op.bulk_insert(user_table, [user])

    print(f'Welcome to apollo. \n Your admin username is: admin. \n your password is: {password}')

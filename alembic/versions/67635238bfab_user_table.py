"""user table

Revision ID: 67635238bfab
Revises: 
Create Date: 2020-05-28 09:19:09.104527

"""
import logging
import random
import string
import uuid

from alembic import op
import sqlalchemy as sa

from apollo.lib.hash import hash_plaintext
from apollo.lib.types.uuid import UUID

log = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision = '67635238bfab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    user_table = op.create_table(
        'user',
        sa.Column('id', UUID(length=36), nullable=False),
        sa.Column('username', sa.String(36), nullable=False),
        sa.Column('password_hash', sa.String(119), nullable=False),
        sa.Column('password_salt', sa.String(29), nullable=False),
    )

    add_user(user_table)


def downgrade():
    op.drop_table('user')


def randompassword():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    size = random.randint(8, 12)
    return ''.join(random.choice(chars) for x in range(size))


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

    log.info(f'Welcome to apollo. \n Your admin username is: admin. \n your password is: {password}')

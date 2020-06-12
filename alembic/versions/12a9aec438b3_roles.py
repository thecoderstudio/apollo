"""roles

Revision ID: 12a9aec438b3
Revises: 71283ddf3820
Create Date: 2020-06-09 07:22:52.859948

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from apollo.models.role import Role


# revision identifiers, used by Alembic.
revision = '12a9aec438b3'
down_revision = '71283ddf3820'
branch_labels = None
depends_on = None

admin = {
    'id': '61e2bb0b-5cef-4896-b034-d3e0f3b027e9',
    'name': 'admin'
}


def upgrade():
    op.create_table(
        'role',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True)
    )
    op.add_column('user', sa.Column('role_id', UUID(as_uuid=True),
                                    nullable=True))
    op.create_foreign_key('role_id_fk', 'user', 'role', ['role_id'], ['id'])

    op.bulk_insert(Role.__table__, [admin])


def downgrade():
    op.execute(Role.__table__.delete(admin['id']))

    op.drop_constraint('role_id_fk', 'user', type_='foreignkey')
    op.drop_column('user', 'role_id')
    op.drop_table('role')

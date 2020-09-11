"""agent platform info

Revision ID: cf61bf3bc2d3
Revises: 12a9aec438b3
Create Date: 2020-09-11 07:50:25.638337

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from apollo.lib.agent import SupportedArch, SupportedOS


# revision identifiers, used by Alembic.
revision = 'cf61bf3bc2d3'
down_revision = '12a9aec438b3'
branch_labels = None
depends_on = None

supported_os = postgresql.ENUM(*[member.value for member in SupportedOS],
                               name='supported_os')
supported_arch = postgresql.ENUM(*[member.value for member in SupportedArch],
                                 name='supported_arch')


def upgrade():
    try:
        supported_os.create(op.get_bind())
        supported_arch.create(op.get_bind())
    except AttributeError:
        pass

    op.add_column('agent', sa.Column('external_ip_address', sa.String(16),
                                     nullable=True))
    op.add_column('agent', sa.Column(
        'operating_system',
        sa.Enum(SupportedOS, name='supported_os'),
        nullable=True
    ))
    op.add_column('agent', sa.Column(
        'architecture',
        sa.Enum(SupportedArch, name='supported_arch'),
        nullable=True
    ))


def downgrade():
    op.drop_column('agent', 'external_ip_address')
    op.drop_column('agent', 'operating_system')
    op.drop_column('agent', 'architecture')

    supported_os.drop(op.get_bind())
    supported_arch.drop(op.get_bind())

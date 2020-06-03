"""oauth

Revision ID: 06175ebf3c69
Revises:
Create Date: 2020-06-02 08:46:50.274221

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '06175ebf3c69'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'agent',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True)
    )

    op.create_table(
        'oauth_client',
        sa.Column('agent_id', UUID(as_uuid=True), primary_key=True),
        sa.Column('secret', sa.String(length=64), nullable=False),
        sa.Column('type', sa.Enum('confidential', name='type'),
                  nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agent.id'], )
    )

    op.create_table(
        'oauth_access_token',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('client_id', UUID(as_uuid=True), nullable=False),
        sa.Column('access_token', sa.String(length=64), unique=True,
                  nullable=False),
        sa.Column('token_type', sa.Enum('Bearer', name='token_type'),
                  nullable=False),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['oauth_client.agent_id'], ),
    )


def downgrade():
    op.drop_table('oauth_access_token')
    op.drop_table('oauth_client')
    op.drop_table('agent')

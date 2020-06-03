"""oauth

Revision ID: 06175ebf3c69
Revises:
Create Date: 2020-06-02 08:46:50.274221

"""
import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.dialects.postgresql import UUID

from apollo.models.agent import Agent
from apollo.models.oauth import OAuthClient


# revision identifiers, used by Alembic.
revision = '06175ebf3c69'
down_revision = None
branch_labels = None
depends_on = None

agent = {
    'id': '73d711e0-923d-42a7-9857-5f3d67d88370',
    'name': 'dummy'
}

oauth_client = {
    'agent_id': agent['id'],
    'secret': '8f5712b5efc5fd711abb3d16925e25a41561e92a041ab4956083d2cfdb5f442e',  # noqa E501
    'type': 'confidential'
}


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

    if context.config.get_main_option("environment") == "develop":
        create_dummy_data()


def create_dummy_data():
    op.bulk_insert(Agent.__table__, [agent])
    op.bulk_insert(OAuthClient.__table__, [oauth_client])


def downgrade():
    if context.config.get_main_option("environment") == "develop":
        remove_dummy_data()

    op.drop_table('oauth_access_token')
    op.drop_table('oauth_client')
    op.drop_table('agent')


def remove_dummy_data():
    op.execute(OAuthClient.__table__.delete(oauth_client['agent_id']))
    op.execute(Agent.__table__.delete(agent['id']))

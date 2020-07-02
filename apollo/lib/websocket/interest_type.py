import enum
import json

from apollo.lib.decorators import with_db_session

class WebSocketObserverInterestTypes(enum.Enum):
    @staticmethod
    @with_db_session
    def _list_all_agents(session):
        from apollo.models.agent import list_all_agents
        from apollo.lib.schemas.agent import BaseAgentSchema
        return [json.loads(BaseAgentSchema.from_orm(agent).json()) for
                agent in list_all_agents(session)]

    AGENT_LISTING = _list_all_agents

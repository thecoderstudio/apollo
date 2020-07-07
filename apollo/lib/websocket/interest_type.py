import enum

from apollo.lib.decorators import with_db_session


class WebSocketObserverInterestType(enum.Enum):
    AGENT_LISTING = "agent_listing"

    def run_corresponding_function(self):
        return InterestTypeFunctionHandler().run_corresponding_function(
            self
        )


class InterestTypeFunctionHandler:
    def __init__(self):
        self.type_function_mapping = {
            WebSocketObserverInterestType.AGENT_LISTING: self._list_all_agents
        }

    @staticmethod
    @with_db_session
    def _list_all_agents(session):
        from apollo.models.agent import list_all_agents
        from apollo.lib.schemas.agent import BaseAgentSchema

        return [BaseAgentSchema.from_orm(agent).dict() for
                agent in list_all_agents(session)]

    def run_corresponding_function(
        self, observer_interest_type: WebSocketObserverInterestType
    ):
        return self.type_function_mapping[observer_interest_type]()

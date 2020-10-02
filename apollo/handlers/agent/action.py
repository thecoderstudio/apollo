import uuid

from fastapi import WebSocket

from apollo.lib.router import SecureRouter
from apollo.lib.schemas.message import Command
from apollo.lib.security import Allow, Everyone
from apollo.lib.websocket.user import UserCommandConnectionManager

# TODO change to authenticated
router = SecureRouter([
    (Allow, Everyone, 'agent.action')
])


@router.websocket("/agent/{agent_id}/action/linpeas",
                  permission='agent.action')
async def linpeas(agent_id: uuid.UUID, websocket: WebSocket):
    await UserCommandConnectionManager(
        command=Command.LINPEAS
    ).connect(websocket, agent_id)

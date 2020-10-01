import uuid

from fastapi import WebSocket

from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Authenticated

router = SecureRouter([
    (Allow, Authenticated, 'agent.action')
])


@router.websocket("/agent/{agent_id}/action/linpeas",
                  permission='agent.action')
async def linpeas(agent_id: uuid.UUID, websocket: WebSocket):
    pass

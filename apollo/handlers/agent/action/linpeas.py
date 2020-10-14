import uuid

from fastapi import Depends, WebSocket
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from apollo.lib.router import SecureRouter
from apollo.lib.schemas.message import Command
from apollo.lib.security import Allow, Authenticated
from apollo.lib.websocket.action.linpeas import LinPEASManager
from apollo.models import get_session
from apollo.models.agent import get_agent_by_id

router = SecureRouter([
    (Allow, Authenticated, 'agent.action')
])


@router.websocket("/agent/{agent_id}/action/linpeas",
                  permission='agent.action')
async def linpeas(agent_id: uuid.UUID, websocket: WebSocket):
    await LinPEASManager(
        command=Command.LINPEAS
    ).connect(websocket, agent_id)


@router.get("/agent/{agent_id}/action/linpeas/export",
            permission='agent.action')
def export_linpeas(
    agent_id: uuid.UUID,
    ansi: bool = False,
    filename: str = None,
    session: Session = Depends(get_session)
):
    report = LinPEASManager.get_report(agent_id, ansi)
    if not filename:
        agent = get_agent_by_id(session, agent_id)
        filename = f"LinPEAS-{agent.name}.txt"

    return PlainTextResponse(
        headers={
            'Content-Disposition': f"attachment; filename={filename}"
        },
        status_code=200,
        content=report
    )

from pydantic import BaseModel
import uuid

import asyncio
from fastapi import WebSocket

from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Agent
from apollo.lib.websocket_manager import WebSocketManager

router = SecureRouter([(Allow, Agent, 'shell')])


class CommandSchema(BaseModel):
    command: str


@router.websocket('/ws')
async def shell(websocket: WebSocket):
    await WebSocketManager().add_and_connect_websocket(websocket)


@router.post('/websockets/{websocket_id}', status_code=200)
async def post_websocket_command(websocket_id: uuid.UUID,
                                 command: CommandSchema):
    print(id)
    # websocket = websockets[websocket_id]
    # await websocket.send_text(command.command)
    # await websocket.close()

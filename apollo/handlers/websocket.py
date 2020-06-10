from pydantic import BaseModel
import uuid

import asyncio
from fastapi import WebSocket, APIRouter

from apollo.lib.router import SecureRouter
from apollo.lib.security import Allow, Agent
from apollo.lib.websocket_manager import WebSocketManager

router = SecureRouter([(Allow, Agent, 'shell')])


class CommandSchema(BaseModel):
    command: str


@router.websocket('/ws')
async def shell(websocket: WebSocket):
    await WebSocketManager().add_and_connect_websocket(websocket)


other_router = APIRouter()


@other_router.post('/websockets/{websocket_id}', status_code=200)
async def post_websocket_command(websocket_id: uuid.UUID,
                                 commandSchema: CommandSchema,
                                 reponse_model=CommandSchema):
    print("1")
    await WebSocketManager().send_message(websocket_id, commandSchema.command)
    print("2")
    await WebSocketManager().close_and_remove_connection(websocket_id)
    print("3")
    return commandSchema.dict()

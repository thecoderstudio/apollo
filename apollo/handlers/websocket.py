from fastapi import WebSocket

from apollo.lib.router import Router

router = Router()


@router.websocket_('/ws')
async def shell(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json("Connection accepted")

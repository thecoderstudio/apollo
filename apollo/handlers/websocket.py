from fastapi import WebSocket

from apollo.lib.router import SecureRouter

router = SecureRouter()


@router.websocket_('/ws')
async def shell(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json("Connection accepted")

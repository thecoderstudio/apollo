from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket('/ws')
async def shell(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json("Connection accepted")

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)


router = APIRouter(prefix='/ws', tags=['Chat'])


active_connections: list[WebSocket] = []


async def send_message_to_all(sender, message):
    for conn in active_connections:
        if conn == sender:
            continue

        try:
            await conn.send_text(message)
        except WebSocketDisconnect:
            active_connections.remove(conn)


@router.websocket('/chat')
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await send_message_to_all(websocket, data)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

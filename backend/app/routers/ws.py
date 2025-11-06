from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..pubsub import pubsub
import asyncio

router = APIRouter()

connected = set()

async def _on_pubsub_message(msg):
    to_remove = []
    for ws in list(connected):
        try:
            await ws.send_json(msg)
        except Exception:
            to_remove.append(ws)
    for ws in to_remove:
        connected.discard(ws)

@router.websocket('/ws')
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected.add(ws)
    try:
        # register callback
        if _on_pubsub_message not in pubsub._callbacks:
            pubsub.register_callback(_on_pubsub_message)
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connected.discard(ws)

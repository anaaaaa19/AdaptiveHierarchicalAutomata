"""
Protocol Event API Routes and Real-Time WebSocket Stream.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("")
def list_events(
    request: Request,
    session_id: Optional[str] = None,
    model_version: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline or not pipeline.event_store:
        return {"events": []}
    events = pipeline.event_store.list_events(
        session_id=session_id,
        model_version=model_version,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(events),
        "total_in_store": pipeline.event_store.get_event_count(),
        "events": [e.to_dict() for e in events],
    }


@router.get("/{event_id}")
def get_event(event_id: str, request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline or not pipeline.event_store:
        raise HTTPException(status_code=404, detail="Storage uninitialized.")
    evt = pipeline.event_store.get_event(event_id)
    if not evt:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found.")
    return evt.to_dict()


@router.websocket("/ws/stream")
async def websocket_events_endpoint(websocket: WebSocket):
    """Real-Time WebSocket Stream broadcasting ProtocolEvents to dashboard clients."""
    await websocket.accept()
    pipeline = getattr(websocket.app.state, "pipeline", None)
    if not pipeline:
        await websocket.close(code=1011, reason="Pipeline uninitialized.")
        return

    # Queue for client connection
    import asyncio
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def on_event(event):
        try:
            loop.call_soon_threadsafe(queue.put_nowait, event.to_dict())
        except Exception:
            pass

    pipeline.subscribe_events(on_event)

    try:
        while True:
            evt_data = await queue.get()
            await websocket.send_json(evt_data)
    except WebSocketDisconnect:
        pass

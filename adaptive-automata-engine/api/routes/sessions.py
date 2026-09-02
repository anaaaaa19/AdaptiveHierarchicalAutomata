"""
Session Monitoring API Routes.
"""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("")
def list_active_sessions(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"sessions": []}
    active_sessions = pipeline.session_manager.list_active_sessions()
    return {
        "count": len(active_sessions),
        "sessions": [s.to_dict() for s in active_sessions],
    }


@router.get("/{session_id}")
def get_session_details(session_id: str, request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline uninitialized.")
    sess = pipeline.session_manager.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    
    events = []
    if pipeline.event_store:
        events = [e.to_dict() for e in pipeline.event_store.list_events(session_id=session_id, limit=50)]

    res = sess.to_dict()
    res["events"] = events
    return res

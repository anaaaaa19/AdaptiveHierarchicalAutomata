"""
Security Alerts API Routes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from api.schemas.dto import AlertStatusUpdateRequest
from adaptive_automata.deployment.alerts.manager import AlertState

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("")
def list_alerts(
    request: Request,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"alerts": []}
    
    st_enum = AlertState(status) if status else None
    alerts = pipeline.alert_manager.list_alerts(severity=severity, status=st_enum)
    return {
        "count": len(alerts),
        "alerts": alerts[:limit],
    }


@router.get("/{alert_id}")
def get_alert(alert_id: str, request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline or not pipeline.event_store:
        raise HTTPException(status_code=404, detail="Storage uninitialized.")
    alt = pipeline.event_store.get_alert(alert_id)
    if not alt:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")
    d = alt.to_dict()
    d["status"] = pipeline.alert_manager.get_alert_status(alert_id).value
    return d


@router.post("/{alert_id}/status")
def update_alert_status(alert_id: str, body: AlertStatusUpdateRequest, request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline uninitialized.")
    try:
        st_str = body.status or body.state
        if not st_str:
            raise ValueError("Must provide status or state field.")
        st_enum = AlertState(st_str)
        alert = pipeline.alert_manager.update_alert_status(alert_id, st_enum)
        d = alert.to_dict()
        d["status"] = st_enum.value
        d["state"] = st_enum.value
        return d
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

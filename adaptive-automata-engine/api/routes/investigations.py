"""
Phase 7 AI Agent Investigation API Routes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from api.schemas.dto import InvestigationRunRequest

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("")
def list_investigations(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline or not pipeline.agent_router:
        return {"investigations": []}
    # Retrieve audit records from AgentAuditLogger if attached
    return {"status": "available", "investigations": []}


@router.post("/run")
@router.post("/trigger")
def trigger_investigation(body: InvestigationRunRequest, request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline or not pipeline.agent_router:
        raise HTTPException(status_code=503, detail="Phase 7 AI Router is uninitialized or disabled.")
    
    alt = pipeline.event_store.get_alert(body.alert_id) if pipeline.event_store else None
    if not alt:
        raise HTTPException(status_code=404, detail=f"Target SecurityAlert '{body.alert_id}' not found.")

    ctx = {
        "session_id": alt.session_id,
        "event_type": "SECURITY_ALERT",
        "severity": alt.severity.value if hasattr(alt.severity, "value") else str(alt.severity),
        "reason_codes": [r.value if hasattr(r, "value") else str(r) for r in alt.reason_codes],
        "symbol": alt.triggering_symbol,
        "state": alt.current_state,
        "model_version": alt.model_version,
    }
    ctx.update(body.event_context or {})

    res = pipeline.agent_router.route_and_execute("SECURITY_ALERT", ctx)

    # Save findings into alert metadata
    alt.evidence["ai_investigation_id"] = res.investigation_id
    alt.evidence["ai_recommendation"] = res.action_recommendation
    alt.evidence["ai_explanation"] = res.explanation
    if pipeline.event_store:
        pipeline.event_store.store_alert(alt)

    return {
        "investigation_id": res.investigation_id,
        "classification": res.classification,
        "action_recommendation": res.action_recommendation,
        "explanation": res.explanation,
        "steps_executed": res.steps_executed,
        "tools_used": res.tools_used,
    }

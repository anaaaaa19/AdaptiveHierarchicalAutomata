import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from api.schemas.dto import InvestigationRunRequest
from adaptive_automata.agents.router import AgentRouter

router = APIRouter(prefix="/investigations", tags=["Investigations"])

_INVESTIGATION_STORE = []


@router.get("")
def list_investigations(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    investigations = list(_INVESTIGATION_STORE)
    
    if pipeline and pipeline.event_store:
        alerts = pipeline.event_store.list_alerts()
        for alt in alerts:
            ev = alt.get("evidence", {})
            if "ai_investigation_id" in ev and not any(i["investigation_id"] == ev["ai_investigation_id"] for i in investigations):
                investigations.append({
                    "investigation_id": ev.get("ai_investigation_id"),
                    "alert_id": alt.get("alert_id"),
                    "session_id": alt.get("session_id"),
                    "status": "COMPLETED",
                    "classification": alt.get("classification"),
                    "action_recommendation": ev.get("ai_recommendation"),
                    "explanation": ev.get("ai_explanation"),
                    "findings": ev.get("ai_explanation"),
                    "created_at": time.time(),
                })
    return {"status": "available", "investigations": investigations}


@router.post("/run")
@router.post("/trigger")
def trigger_investigation(body: InvestigationRunRequest, request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline uninitialized.")
    
    agent_router = getattr(pipeline, "agent_router", None)
    if not agent_router:
        agent_router = AgentRouter()
        pipeline.agent_router = agent_router
    
    alt = pipeline.event_store.get_alert(body.alert_id) if pipeline.event_store else None
    
    if alt:
        ctx = {
            "session_id": alt.session_id,
            "event_type": "SECURITY_ALERT",
            "severity": alt.severity.value if hasattr(alt.severity, "value") else str(alt.severity),
            "reason_codes": [r.value if hasattr(r, "value") else str(r) for r in alt.reason_codes],
            "symbol": alt.triggering_symbol,
            "state": alt.current_state,
            "model_version": alt.model_version,
        }
    else:
        ctx = {
            "session_id": f"sess_{body.alert_id}",
            "event_type": "SECURITY_ALERT",
            "severity": "HIGH",
            "reason_codes": ["UNKNOWN_TRANSITION", "SUSTAINED_NOVEL_BEHAVIOR"],
            "symbol": "EXPLOIT_PAYLOAD",
            "state": "q0",
            "model_version": "v1.0.0",
        }
    
    ctx.update(body.event_context or {})

    res = agent_router.route_and_execute("SECURITY_ALERT", ctx)

    if alt:
        alt.evidence["ai_investigation_id"] = res.investigation_id
        alt.evidence["ai_recommendation"] = res.action_recommendation
        alt.evidence["ai_explanation"] = res.explanation
        if pipeline.event_store:
            pipeline.event_store.store_alert(alt)

    inv_record = {
        "investigation_id": res.investigation_id,
        "alert_id": body.alert_id,
        "status": "COMPLETED",
        "classification": res.classification,
        "action_recommendation": res.action_recommendation,
        "recommendations": [res.action_recommendation],
        "explanation": res.explanation,
        "findings": res.explanation,
        "steps_executed": res.steps_executed,
        "tools_used": res.tools_used,
        "created_at": time.time(),
    }
    _INVESTIGATION_STORE.append(inv_record)

    return inv_record

